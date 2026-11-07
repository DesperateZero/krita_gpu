"""Analyze only the fixed prospective samples; no exclusions or resampling runs."""
from pathlib import Path
import hashlib
import json
import math
import random
import statistics

H = Path(__file__).resolve().parent
protocol = json.loads((H / 'protocol.json').read_text())
median = statistics.median
result = {'product': protocol['product'], 'families': {},
          'analysis_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
for family in ['calibration', 'hit', 'miss']:
    plan = protocol[family]
    rows = json.loads((H / family / 'runs.json').read_text())
    assert len(rows) == plan['buckets'] * 40 * 2
    assert json.loads((H / family / 'identity-final.json').read_text())['inputs_verified']
    assert all(r['exit_code'] == 0 and r['loaded'] and r['reaped'] and not r['timed_out'] and not r['failures'] for r in rows)
    values = []
    for arch in plan['architectures']:
        for k in plan['K']:
            for case in plan['cases']:
                group = [r for r in rows if (r['arch'],r['K'],r['case']) == (arch,k,case)]
                logs, baseline, candidate, absolute_ns = [], [], [], []
                for pair in range(40):
                    records = {r['image'] if family == 'calibration' else r['variant']:r for r in group if r['pair'] == pair}
                    base, test = (records['production'], records['selection']) if family == 'calibration' else (records['off'], records['on'])
                    baseline.append(base['median_ns']); candidate.append(test['median_ns'])
                    absolute_ns.append(base['median_ns'] - test['median_ns'])
                    logs.append(math.log(base['median_ns']/test['median_ns']) if family == 'hit'
                                else math.log(test['throughput']/base['throughput']))
                units = logs if family == 'hit' else [(logs[i]+logs[i+1])/2 for i in range(0,40,2)]
                rng = random.Random(plan['seed'])
                boot = sorted(median(rng.choices(units, k=len(units))) for _ in range(plan['bootstrap']))
                alpha = ((1-plan['two_sided_confidence'])/2 if family == 'calibration'
                         else 1-plan['one_sided_confidence'])
                low, high = boot[int(alpha*len(boot))], boot[min(len(boot)-1,int((1-alpha)*len(boot)))]
                transform = (lambda x: 1-math.exp(-x)) if family == 'hit' else math.exp
                point, lower, upper = transform(median(units)), transform(low), transform(high)
                passed = (lower > 0 if family == 'hit' else
                          lower >= .98 and upper <= 1.02 if family == 'calibration' else lower >= .98)
                values.append(dict(arch=arch, K=k, case=case, pairs=40, statistical_units=len(units),
                    metric='latency_reduction' if family == 'hit' else 'completed_operation_throughput_ratio',
                    point=point, lower=lower, upper=upper, passes=passed,
                    baseline_marginal_median_us=median(baseline)/1000,
                    candidate_marginal_median_us=median(candidate)/1000,
                    paired_median_saving_us=median(absolute_ns)/1000,
                    observed_hits=sorted({h for r in group for h in r['hits']})))
    result['families'][family] = dict(processes=len(rows), passed=all(v['passes'] for v in values), rows=values)
for family in ['fixed-m5-fresh', 'fixed-m5-history']:
    data = json.loads((H / (family + '-summary.json')).read_text())
    result['families'][family] = data
preflight = json.loads((H / 'preflight/runs.json').read_text())
result['preflight'] = {'processes':len(preflight), 'safety':[], 'capacity':[], 'generations':[]}
for r in preflight:
    if r['safety']:
        result['preflight']['safety'].append({k:r[k] for k in ['arch','image','totals','exit_code']})
    elif r['tight'] or r['rounds'] == 4:
        samples = [json.loads(x) for x in (H / 'preflight' / r['log']).read_text().splitlines() if x.startswith('{"case"')]
        result['preflight']['capacity' if r['tight'] else 'generations'].append(
            dict(arch=r['arch'], case=r['case'], variant=r['variant'], samples=samples))
result['qualification'] = {
    'same_image_hit': result['families']['hit']['passed'],
    'same_image_miss': result['families']['miss']['passed'],
    'selection_image_equivalence': result['families']['calibration']['passed'],
    'M6_complete': False,
    'remaining': ['Metadata >=25% comparable pre-reconstruction used/reserved/slack denominator is not supplied by these performance samples.',
                  'CP0 complete required inventory/build qualification and real natural producer/trace coverage remain separately audited.',
                  'No GPU performance, M7/M8 or business default qualification.']}
(H / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
for family in ['calibration','hit','miss']:
    print(family, result['families'][family]['passed'])
    for row in result['families'][family]['rows']:
        print(row['arch'],row['K'],row['case'],round(row['point'],5),round(row['lower'],5),round(row['upper'],5),row['passes'])
