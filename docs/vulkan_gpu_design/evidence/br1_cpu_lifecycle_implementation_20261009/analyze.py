#!/usr/bin/env python3
"""Predeclared uninstrumented block comparisons, all samples retained."""
import json,math,random,statistics
from pathlib import Path
H=Path(__file__).resolve().parent
def quantile(v,q):
    p=(len(v)-1)*q;i=int(p);return v[i]+(v[min(i+1,len(v)-1)]-v[i])*(p-i)
for batch in ['parent','upstream','original']:
    path=H/('runs-'+batch)/'results.json'
    if not path.exists():continue
    rows=json.loads(path.read_text());assert len(rows)==80 and all(r['passed'] for r in rows)
    result=dict(blocks=20,bootstrap=20000,seed=261021,interval='pointwise two-sided95%; no formal family qualification',endpoints={},
        workload_variations=[dict(index=r['index'],side=r['side'],updates=r['sample']['projection_updates']) for r in rows if r['sample']['projection_updates']!=19])
    for phase in ['Setup','Stroke','Undo','Redo','Teardown','Lifecycle']:
        for metric in ['wall_ns','cpu_ns']:
            pairs=[]
            for i in range(0,80,2):
                p={r['side']:(sum(s[metric] for s in r['stages']) if phase=='Lifecycle'
                    else next(s[metric] for s in r['stages'] if s['stage']==phase)) for r in rows[i:i+2]};pairs.append((p[batch],p['candidate']))
            logs=[math.log(b/a) for a,b in pairs];blocks=[statistics.mean(logs[i:i+2]) for i in range(0,40,2)]
            rng=random.Random(261021);resamples=sorted(statistics.mean(rng.choices(blocks,k=20)) for _ in range(20000))
            lo,hi=math.exp(quantile(resamples,.025)),math.exp(quantile(resamples,.975))
            result['endpoints'][phase+'/'+metric]=dict(candidate_over_baseline=math.exp(statistics.mean(blocks)),ratio_ci=[lo,hi],
                reduction=1-math.exp(statistics.mean(blocks)),reduction_ci=[1-hi,1-lo],
                baseline_median_ns=statistics.median(a for a,b in pairs),candidate_median_ns=statistics.median(b for a,b in pairs),
                paired_saving_median_ns=statistics.median(a-b for a,b in pairs),control_pass=hi<=1.02,blocks=blocks)
    (H/(batch+'-summary.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(batch)
    for n,v in result['endpoints'].items():print(n,round(100*v['reduction'],2),[round(100*x,2) for x in v['reduction_ci']],round(v['paired_saving_median_ns']/1e6,3))
