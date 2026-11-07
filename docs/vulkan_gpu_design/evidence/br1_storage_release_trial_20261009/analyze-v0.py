#!/usr/bin/env python3
import hashlib, json, re, statistics, subprocess
from pathlib import Path
H = Path(__file__).resolve().parent
rows = json.loads((H / 'micro-run/result.json').read_text())['rows']
assert len(rows) == 256 and all(r['returned_bytes'] == r['capacity'] * r['frees'] for r in rows)
prices = []
for case in range(8):
    subset = [r for r in rows if r['case'] == case]
    delta = []
    for block in range(8):
        means = [statistics.mean(r['cpu_ns'] / r['frees'] for r in subset if r['block'] == block and r['mode'] == mode) for mode in [0, 1]]
        delta.append(means[0] - means[1])
    prices.append(dict(case=case, bytes=subset[0]['bytes'], alignment=subset[0]['alignment'], saving_ns_per_free=statistics.median(delta), block_range=[min(delta), max(delta)], blocks=delta))
raw = (H / 'census-run/00-A/fixture.log').read_text()
check = json.loads(re.search(r'BR1_RELEASE_TRACE_CHECK (\{[^\n]+\})', raw).group(1))
assert check == {'used': 320, 'overflow': 0}
frames = re.findall(r'^BR1_RELEASE_TRACE (\d+) (\d+) (\d+) (\S+) (\+\d+)$', raw, re.M)
symbols = sorted({f[3] for f in frames})
demangled = subprocess.check_output(['/usr/bin/c++filt'], input='\n'.join('_' + s for s in symbols) + '\n', text=True).splitlines()
names = dict(zip(symbols, demangled)); traces = {}
for i, stage, frame, symbol, offset in frames:
    trace = traces.setdefault(i, dict(id=int(i), stage=int(stage), frames=[]))
    trace['frames'].append(dict(frame=int(frame), symbol=symbol, function=names[symbol], offset=offset))
stroke = [t for t in traces.values() if t['stage'] == 2]
history = [t for t in stroke if any('KisPageHistoryCollector::collectSliceLocked(' in f['function'] for f in t['frames'])]
work = [t for t in history if any('KisPageHistoryCollector::Work' in f['function'] and 'erase(' in f['function'] for f in t['frames'])]
(H / 'census-demangled.json').write_text(json.dumps(list(traces.values()), indent=2) + '\n')
result = dict(micro_prices=prices, census=dict(total=len(traces), stroke=len(stroke), history_slices=len(history), work_erase=len(work), overflow=0), limits='Systematic release-event sample, not CPU sampling or unbiased proportion; micro prices conditional, not an end-to-end CI')
result['input_hashes'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [H / 'micro-run/result.json', H / 'census-run/00-A/fixture.log', Path(__file__)]}
(H / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result['census']))
for row in prices: print(row['bytes'], row['alignment'], row['saving_ns_per_free'])
