#!/usr/bin/env python3
"""Exclusive CPU accounting, mode perturbation, and previous-coverage bridge."""
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

H = Path(__file__).resolve().parent
MODES = ('original', 'off', 'jobs', 'detail')
SIDES = ('current', 'upstream')
CORE = {'cold', 'seal', 'commit', 'capture', 'operation', 'proj_merge'}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows = json.loads((H/'matrix/results.json').read_text())
assert len(rows) == 64 and all(r['passed'] for r in rows)


def stats(values):
    return dict(mean=statistics.mean(values), median=statistics.median(values),
                minimum=min(values), maximum=max(values), values=values)


processes = []
for row in rows:
    stage = next(s for s in row['stages'] if s['stage'] == 'Stroke')
    events = [e for e in row['events'] if e['stage'] == 2]
    by_id = {e['id']: e for e in events}
    children = defaultdict(list)
    for event in events:
        assert event['end_stage'] == 2
        if event['parent']:
            assert event['parent'] in by_id
            parent = by_id[event['parent']]
            assert parent['thread'] == event['thread']
            children[event['parent']].append(event)
    for event in events:
        assert event['cpu_ns'] == event['self_cpu_ns'] + sum(c['cpu_ns'] for c in children[event['id']])
        assert event['end_ns']-event['start_ns'] == event['self_wall_ns'] + sum(c['end_ns']-c['start_ns'] for c in children[event['id']])

    def lineage(event):
        names, seen = [], set()
        while event:
            assert event['id'] not in seen
            seen.add(event['id'])
            names.append(event['name'])
            event = by_id.get(event['parent'])
        return names

    coarse = defaultdict(int)
    buckets = defaultdict(int)
    contexts = defaultdict(lambda: defaultdict(int))
    counts = defaultdict(lambda: defaultdict(int))
    bridge = defaultdict(int)
    prior_covered = 0
    for event in events:
        chain = lineage(event)
        job = next((n for n in chain if n.startswith('job_')), 'nonjob_observed')
        coarse[job] += event['self_cpu_ns']
        family = next((n for n in chain if n in ('cold', 'seal', 'commit', 'capture')), None)
        if family is None:
            family = next((n for n in chain if n in ('pixel_callback', 'operation', 'proj_merge')), 'job_or_other_residual')
        context = 'projection' if 'proj_merge' in chain else job
        buckets[family] += event['self_cpu_ns']
        contexts[context][family] += event['self_cpu_ns']
        counts[context][event['name']] += 1
        if CORE.intersection(chain):
            prior_covered += event['self_cpu_ns']
        else:
            bridge[job] += event['self_cpu_ns']
    root_cpu = sum(e['cpu_ns'] for e in events if not e['parent'])
    assert root_cpu == sum(coarse.values()) == sum(buckets.values())
    residual = stage['cpu_ns'] - root_cpu
    assert residual >= 0
    assert prior_covered + sum(bridge.values()) + residual == stage['cpu_ns']
    coarse['uncovered'] = residual
    bridge['uncovered'] = residual
    ms = lambda x: {k: v/1e6 for k, v in sorted(x.items())}
    processes.append(dict(index=row['index'], block=row['block'], configuration=row['configuration'], side=row['side'],
                          process_cpu_ms=stage['cpu_ns']/1e6, wall_ms=stage['wall_ns']/1e6,
                          user_ms=stage['user_ns']/1e6, system_ms=stage['system_ns']/1e6,
                          projection_updates=row['sample']['projection_updates'],
                          coarse_ms=ms(coarse), detail_ms=ms(buckets), contexts_ms={k: ms(v) for k, v in contexts.items()},
                          counts={k: dict(sorted(v.items())) for k, v in counts.items()},
                          prior_main_scopes_ms=prior_covered/1e6,
                          outside_prior_main_scopes_ms=(stage['cpu_ns']-prior_covered)/1e6,
                          coverage_bridge_ms=ms(bridge)))

summaries = {}
for mode in MODES:
    selected = [r for r in processes if r['configuration'] == mode]
    assert len(selected) == 16
    report = {}
    for side in SIDES:
        side_rows = [r for r in selected if r['side'] == side]
        assert len(side_rows) == 8
        report[side] = {field: stats([r[field] for r in side_rows]) for field in
                        ('process_cpu_ms', 'wall_ms', 'user_ms', 'system_ms', 'prior_main_scopes_ms', 'outside_prior_main_scopes_ms')}
        for field in ['coarse_ms', 'detail_ms', 'coverage_bridge_ms']:
            keys = sorted({key for r in side_rows for key in r[field]})
            report[side][field] = {key: stats([r[field].get(key, 0) for r in side_rows]) for key in keys}
        report[side]['counts'] = {context: {name: sorted({r['counts'].get(context, {}).get(name, 0) for r in side_rows})
                                 for name in {n for r in side_rows for n in r['counts'].get(context, {})}}
                                 for context in {c for r in side_rows for c in r['counts']}}
    coarse_keys = sorted({key for r in selected for key in r['coarse_ms']})
    paired = defaultdict(list)
    block_differences = []
    for block in range(4):
        batch = [r for r in selected if r['block'] == block]
        assert [r['side'] for r in batch] == ['current', 'upstream', 'upstream', 'current']
        for i in [0, 2]:
            pair = {r['side']: r for r in batch[i:i+2]}
            for field in ['process_cpu_ms', 'wall_ms', 'user_ms', 'system_ms']:
                paired[field].append(pair['current'][field]-pair['upstream'][field])
            for key in coarse_keys:
                paired[key].append(pair['current']['coarse_ms'].get(key, 0)-pair['upstream']['coarse_ms'].get(key, 0))
        block_differences.append({key: statistics.mean(values[-2:]) for key, values in paired.items()})
    report['paired_extra'] = {key: stats(values) for key, values in paired.items()}
    report['block_extra'] = block_differences
    assert abs(sum(report['paired_extra'][k]['mean'] for k in coarse_keys)-report['paired_extra']['process_cpu_ms']['mean']) < 1e-9
    summaries[mode] = report

perturbation = []
for before, after in [('original', 'off'), ('off', 'jobs'), ('jobs', 'detail')]:
    record = dict(before=before, after=after)
    for side in SIDES:
        values = []
        for block in range(4):
            mean = lambda mode: statistics.mean(r['process_cpu_ms'] for r in processes if r['block'] == block and r['configuration'] == mode and r['side'] == side)
            values.append(mean(after)-mean(before))
        record[side+'_block_cpu_change_ms'] = stats(values)
    record['differential_change_ms'] = summaries[after]['paired_extra']['process_cpu_ms']['mean']-summaries[before]['paired_extra']['process_cpu_ms']['mean']
    perturbation.append(record)

result = dict(schema=1, product='704d96e81cf29d16191bc3db8785859d79775e27', upstream='9a24ae0d8c070884fb013594191002e1a1b39a19',
              method='Four fixed balanced blocks per mode. Descriptive same-mode means and paired differences only; no new probability interval or qualification. Clock/layout costs not subtracted.',
              inputs={n: sha(H/n) for n in ['PROTOCOL.md', 'run.py', 'matrix/results.json', 'matrix/identity-final.json', 'capability/results.json']},
              summaries=summaries, perturbation=perturbation, processes=processes)
(H/'summary.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
for mode, report in summaries.items():
    print('\nMODE', mode)
    print('process means', {side: report[side]['process_cpu_ms']['mean'] for side in SIDES})
    print('extra means', {name: round(v['mean'], 6) for name, v in report['paired_extra'].items()})
    if mode == 'detail':
        print('current buckets', {k: round(v['mean'], 6) for k, v in report['current']['detail_ms'].items()})
        print('current coverage bridge', {k: round(v['mean'], 6) for k, v in report['current']['coverage_bridge_ms'].items()})
print('\nMODE CHANGES', json.dumps(perturbation, indent=2))
