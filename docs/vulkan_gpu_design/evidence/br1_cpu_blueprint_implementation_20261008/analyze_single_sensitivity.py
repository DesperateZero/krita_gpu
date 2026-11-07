#!/usr/bin/env python3
"""Post-hoc same-update sensitivity; primary sample and report remain intact."""
import json
import math
import random
import statistics
from pathlib import Path

H = Path(__file__).resolve().parent
rows = json.loads((H / 'runs-single-candidate/results.json').read_text())
assert len(rows) == 16 and all(r['passed'] for r in rows)
changed = sorted({r['index'] // 4 for r in rows if r['sample']['projection_updates'] != 19})
assert changed == [1]


def estimate(stage, metric, excluded):
    blocks = []
    for block in range(4):
        if block in excluded:
            continue
        ratios = []
        for offset in [0, 2]:
            pair = {r['side']: r for r in rows[block * 4 + offset:block * 4 + offset + 2]}
            v = {side: next(s[metric] for s in row['stages'] if s['stage'] == stage)
                 for side, row in pair.items()}
            ratios.append(math.log(v['candidate'] / v['parent']))
        blocks.append(statistics.mean(ratios))
    rng = random.Random(261028)
    samples = sorted(statistics.mean(rng.choices(blocks, k=len(blocks))) for _ in range(20000))
    def q(p):
        x = (len(samples) - 1) * p
        i = int(x)
        return samples[i] + (samples[min(i + 1, len(samples) - 1)] - samples[i]) * (x - i)
    return dict(blocks=len(blocks), reduction=1-math.exp(statistics.mean(blocks)),
                ci_low=1-math.exp(q(.975)), ci_high=1-math.exp(q(.025)))


result = dict(primary_preserved=True, post_hoc=True, excluded_blocks=changed,
              reason='One candidate process index6 had18 projection updates; remove its entire ABBA block only for sensitivity',
              scope='Not a replacement estimate, not a new pass, no additional processes', endpoints={})
for stage in ['Stroke', 'Undo', 'Redo', 'Teardown']:
    for metric in ['wall_ns', 'cpu_ns']:
        result['endpoints'][stage + '/' + metric] = estimate(stage, metric, changed)
(H / 'single-sensitivity-summary.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
