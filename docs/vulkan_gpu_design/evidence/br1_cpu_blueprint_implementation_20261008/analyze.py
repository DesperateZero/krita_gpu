#!/usr/bin/env python3
"""Finite paired timing and diagnostic work; no sample exclusion or new runs."""
import argparse
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

H = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('batch', choices=['switch', 'candidate', 'upstream'], default='switch', nargs='?')
args = parser.parse_args()
rows = json.loads((H / ('runs-' + args.batch) / 'results.json').read_text())
assert all(r['passed'] for r in rows)
parent, candidate = {'switch': ('legacy', 'block'), 'candidate': ('parent', 'candidate'), 'upstream': ('upstream', 'candidate')}[args.batch]
assert len(rows) == (16 if args.batch == 'upstream' else 48)


def quantile(values, q):
    position = (len(values) - 1) * q
    i = int(position)
    return values[i] + (values[min(i + 1, len(values) - 1)] - values[i]) * (position - i)


result = dict(pairs=len(rows) // 2, blocks=len(rows) // 4, bootstrap=20000, seed=261028,
              interval='pointwise two-sided95%, block log ratios; no family adjustment',
              interpretation='local control only, no formal M6 qualification', endpoints={},
              workload_variations=[{'index': r['index'], 'side': r['side'], 'projection_updates': r['sample']['projection_updates']}
                                   for r in rows if r['sample']['projection_updates'] != 19])
for phase in ['Stroke', 'Undo', 'Redo', 'Teardown']:
    for metric in ['wall_ns', 'cpu_ns']:
        pairs, logs = [], []
        for i in range(0, len(rows), 2):
            pair = {r['side']: r for r in rows[i:i + 2]}
            assert set(pair) == {parent, candidate}
            av = next(s[metric] for s in pair[parent]['stages'] if s['stage'] == phase)
            bv = next(s[metric] for s in pair[candidate]['stages'] if s['stage'] == phase)
            pairs.append((av, bv))
            logs.append(math.log(bv / av))
        blocks = [statistics.mean(logs[i:i + 2]) for i in range(0, len(logs), 2)]
        rng = random.Random(261028)
        samples = sorted(statistics.mean(rng.choices(blocks, k=len(blocks))) for _ in range(20000))
        result['endpoints'][phase + '/' + metric] = dict(
            reduction=1 - math.exp(statistics.mean(blocks)),
            ci_low=1 - math.exp(quantile(samples, .975)), ci_high=1 - math.exp(quantile(samples, .025)),
            parent_median_ns=statistics.median(a for a, b in pairs), candidate_median_ns=statistics.median(b for a, b in pairs),
            paired_saving_median_ns=statistics.median(a - b for a, b in pairs), block_log_ratios=blocks)
(H / (args.batch + '-summary.json')).write_text(json.dumps(result, indent=2) + '\n')
print(args.batch, 'variations', result['workload_variations'])
for name, value in result['endpoints'].items():
    print(name, 'reduction %.2f%% [%.2f, %.2f]; paired saving %.3f ms' % (
        value['reduction'] * 100, value['ci_low'] * 100, value['ci_high'] * 100, value['paired_saving_median_ns'] / 1e6))

if args.batch == 'switch':
    diagnostic = []
    for row in json.loads((H / 'runs-diagnostic/results.json').read_text()):
        events = row['events']
        byid = {e['id']: e for e in events}
        assert len(byid) == len(events)
        children, stages, boundaries = defaultdict(list), {}, []
        for e in events:
            assert e['stage'] == e['end_stage']
            if e['parent']:
                p = byid[e['parent']]
                assert p['thread'] == e['thread'] and p['start_ns'] <= e['start_ns'] <= e['end_ns'] <= p['end_ns']
                children[e['parent']].append(e)
        for e in events:
            assert e['self_cpu_ns'] + sum(c['cpu_ns'] for c in children[e['id']]) == e['cpu_ns']
            assert e['self_wall_ns'] + sum(c['end_ns'] - c['start_ns'] for c in children[e['id']]) == e['end_ns'] - e['start_ns']
        for index, stage in enumerate(row['stages'], 1):
            selected = [e for e in events if e['stage'] == index]
            names = defaultdict(lambda: dict(calls=0, inclusive_cpu_ns=0, exclusive_cpu_ns=0))
            for e in selected:
                v = names[e['name']]
                v['calls'] += 1
                v['inclusive_cpu_ns'] += e['cpu_ns']
                v['exclusive_cpu_ns'] += e['self_cpu_ns']
                if not stage['start_ns'] <= e['start_ns'] <= e['end_ns'] <= stage['end_ns']:
                    boundaries.append({'stage': stage['stage'], 'event': e})
            covered = sum(e['cpu_ns'] for e in selected if not e['parent'])
            stages[stage['stage']] = dict(cpu_ns=stage['cpu_ns'], covered_cpu_ns=covered,
                                          residual_cpu_ns=stage['cpu_ns'] - covered, names=dict(names))
        diagnostic.append(dict(index=row['index'], side=row['side'], stages=stages, boundary_exceptions=boundaries,
                               projection_updates=row['sample']['projection_updates']))
    (H / 'diagnostic-summary.json').write_text(json.dumps(diagnostic, indent=2) + '\n')
    print('Undo diagnostic:')
    names = sorted({name for row in diagnostic for name in row['stages']['Undo']['names']})
    changes = []
    for name in names:
        values = {side: [r['stages']['Undo']['names'].get(name, dict(calls=0, exclusive_cpu_ns=0))
                         for r in diagnostic if r['side'] == side] for side in ['legacy', 'block']}
        delta = statistics.mean(v['exclusive_cpu_ns'] for v in values['block']) - statistics.mean(v['exclusive_cpu_ns'] for v in values['legacy'])
        changes.append((abs(delta), name, delta, {side: [v['calls'] for v in seq] for side, seq in values.items()}))
    for _, name, delta, counts in sorted(changes, reverse=True)[:12]:
        print(name, 'delta_cpu_us', round(delta / 1000, 3), counts)
    print('Undo counts equal across all four:', all(Counter({k: v['calls'] for k, v in r['stages']['Undo']['names'].items()}) ==
          Counter({k: v['calls'] for k, v in diagnostic[0]['stages']['Undo']['names'].items()}) for r in diagnostic))
