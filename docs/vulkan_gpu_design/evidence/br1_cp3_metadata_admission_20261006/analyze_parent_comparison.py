"""Frozen paired-block estimates, not a new qualification gate."""
import json
import math
from pathlib import Path
import random
import statistics as st

HERE = Path(__file__).resolve().parent
rows = json.loads((HERE / 'parent-comparison/runs.json').read_text())
assert len(rows) == 320 and all(r['exit_code'] == 0 and r['reaped'] and r['image_loaded'] for r in rows)
rng = random.Random(260926)
output = []
for arch in ['arm64', 'x86_64']:
    for k in [1, 16]:
        measures = {key: [] for key in ['throughput_ratio', 'cpu_ratio', 'cpu_saving_us', 'wall_saving_us']}
        levels = {v: {'cpu_us': [], 'wall_us': []} for v in ['parent', 'current']}
        for pair in range(40):
            data = {r['variant']: r['data'][0] for r in rows if (r['arch'], r['K'], r['pair']) == (arch, k, pair)}
            cpu = {v: d['thread_cpu_ns'] / d['completed_operations'] / 1000 for v, d in data.items()}
            wall = {v: d['wall_ns'] / d['completed_operations'] / 1000 for v, d in data.items()}
            measures['throughput_ratio'].append(math.log(wall['parent'] / wall['current']))
            measures['cpu_ratio'].append(math.log(cpu['current'] / cpu['parent']))
            measures['cpu_saving_us'].append(cpu['parent'] - cpu['current'])
            measures['wall_saving_us'].append(wall['parent'] - wall['current'])
            for v in levels:
                levels[v]['cpu_us'].append(cpu[v]); levels[v]['wall_us'].append(wall[v])
        row = dict(arch=arch, K=k, pairs=40, order_balanced_blocks=20,
                   medians={v: {m: st.median(x) for m, x in vv.items()} for v, vv in levels.items()})
        for name, values in measures.items():
            blocks = [(values[i] + values[i + 1]) / 2 for i in range(0, 40, 2)]
            bootstrap = sorted(st.median(rng.choices(blocks, k=20)) for _ in range(50000))
            transform = math.exp if name.endswith('_ratio') else lambda x: x
            row[name] = dict(estimate=transform(st.median(blocks)),
                two_sided_95=[transform(bootstrap[1250]), transform(bootstrap[48749])])
        output.append(row)
result = dict(scope='Matched parent57e59e6 versus metadata admission cache candidate; per-bucket descriptive95% intervals, no family qualification',
              inputs_verified=json.loads((HERE / 'parent-comparison/identity-final.json').read_text())['inputs_verified'], rows=output)
(HERE / 'parent-comparison-summary.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result), flush=True)
