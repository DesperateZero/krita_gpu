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
parser.add_argument('batch', choices=['retained-candidate'], default='retained-candidate', nargs='?')
args = parser.parse_args()
rows = json.loads((H / ('runs-' + args.batch) / 'results.json').read_text())
assert all(r['passed'] for r in rows)
parent, candidate = ('parent', 'candidate')
assert len(rows) == 16


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

