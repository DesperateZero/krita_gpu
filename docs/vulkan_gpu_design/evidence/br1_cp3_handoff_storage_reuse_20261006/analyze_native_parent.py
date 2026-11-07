"""Predeclared paired two-process order blocks, all successful rows retained."""
from pathlib import Path
import json
import math
import random
import statistics as st

HERE = Path(__file__).resolve().parent
runs = json.loads((HERE / 'native-parent/runs.json').read_text())
assert len(runs) == 640 and all(r['exit_code'] == 0 and r['reaped'] and r['checks_passed'] for r in runs)
rng = random.Random(260926)
rows = []
for arch in ['arm64', 'x86_64']:
    for k in [1, 16]:
        for plan in ['fresh', 'handoff']:
            measures = {'reduction': [], 'saving_us': []}
            levels = {v: [] for v in ['parent', 'current']}
            for pair in range(40):
                values = {r['variant']: r['median_ns'] for r in runs
                          if (r['arch'], r['K'], r['plan'], r['pair']) == (arch, k, plan, pair)}
                measures['reduction'].append(math.log(values['parent'] / values['current']))
                measures['saving_us'].append((values['parent'] - values['current']) / 1000)
                for v, x in values.items(): levels[v].append(x / 1000)
            row = dict(arch=arch, K=k, plan=plan, pairs=40, independent_order_blocks=20,
                       marginal_medians_us={v: st.median(x) for v, x in levels.items()})
            for name, values in measures.items():
                blocks = [(values[i] + values[i + 1]) / 2 for i in range(0, 40, 2)]
                samples = sorted(st.median(rng.choices(blocks, k=20)) for _ in range(50000))
                transform = (lambda x: 1 - math.exp(-x)) if name == 'reduction' else lambda x: x
                row[name] = dict(estimate=transform(st.median(blocks)), two_sided_95=[transform(samples[1250]), transform(samples[48749])])
            rows.append(row)
contrasts = []
for arch in ['arm64', 'x86_64']:
    for k in [1, 16]:
        values = {name: [] for name in ['extra_log_gain', 'extra_saving_us']}
        for pair in range(40):
            x = {(r['plan'], r['variant']): r['median_ns'] for r in runs
                 if (r['arch'], r['K'], r['pair']) == (arch, k, pair)}
            gain = {p: math.log(x[p, 'parent'] / x[p, 'current']) for p in ['fresh', 'handoff']}
            saving = {p: (x[p, 'parent'] - x[p, 'current']) / 1000 for p in ['fresh', 'handoff']}
            values['extra_log_gain'].append(gain['handoff'] - gain['fresh'])
            values['extra_saving_us'].append(saving['handoff'] - saving['fresh'])
        row = dict(arch=arch, K=k)
        for name, observations in values.items():
            blocks = [(observations[i] + observations[i + 1]) / 2 for i in range(0, 40, 2)]
            samples = sorted(st.median(rng.choices(blocks, k=20)) for _ in range(50000))
            row[name] = dict(estimate=st.median(blocks), two_sided_95=[samples[1250], samples[48749]])
        contrasts.append(row)
result = dict(scope='Matched native parent0a00bd versus original handoff slot reuse; descriptive per-bucket95% intervals, not stage family qualification',
              rows=rows, handoff_minus_fresh_incremental_contrast=contrasts)
(HERE / 'native-parent-summary.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result), flush=True)
