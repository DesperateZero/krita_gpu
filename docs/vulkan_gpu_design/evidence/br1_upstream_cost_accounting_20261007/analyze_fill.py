#!/usr/bin/env python3
import json,math,random,statistics
from pathlib import Path
H=Path(__file__).resolve().parent
rows=json.loads((H/'fill/results.json').read_text())
assert len(rows)==48 and all(r['passed'] for r in rows)
def quantile(v,q):
    p=(len(v)-1)*q;i=int(p);return v[i]+(v[min(i+1,len(v)-1)]-v[i])*(p-i)
result={'pairs':24,'blocks':12,'bootstrap':20000,'seed':261021,'interval':'pointwise two-sided95%, block log ratios; no family adjustment','endpoints':{}}
varying_blocks=sorted({i//4 for i,r in enumerate(rows) if r['sample']['projection_updates']!=19})
assert varying_blocks==[9]
result['workload_variation']={'block':9,'process':38,'side':'fill','projection_updates':18,'other_processes_projection_updates':19,'primary_retains_all_48':True}
result['equal_update_sensitivity']={'post_hoc':True,'excluded_complete_blocks':varying_blocks,'pairs':22,'blocks':11,'not_independent_or_formal':True,'endpoints':{}}
for phase in ['Stroke','Undo','Redo','Teardown']:
    for metric in ['wall_ns','cpu_ns']:
        pairs=[];logs=[]
        for i in range(0,48,2):
            a,b=sorted(rows[i:i+2],key=lambda x:x['side'])
            assert a['side']=='current' and b['side']=='fill'
            av=next(x[metric] for x in a['stages'] if x['stage']==phase)
            bv=next(x[metric] for x in b['stages'] if x['stage']==phase)
            pairs.append((av,bv));logs.append(math.log(bv/av))
        blocks=[statistics.mean(logs[i:i+2]) for i in range(0,24,2)]
        rng=random.Random(261021)
        samples=sorted(statistics.mean(rng.choices(blocks,k=12)) for _ in range(20000))
        result['endpoints'][phase+'/'+metric]={
            'reduction':1-math.exp(statistics.mean(blocks)),
            'ci_low':1-math.exp(quantile(samples,.975)),
            'ci_high':1-math.exp(quantile(samples,.025)),
            'parent_median_ns':statistics.median(a for a,b in pairs),
            'variant_median_ns':statistics.median(b for a,b in pairs),
            'paired_saving_median_ns':statistics.median(a-b for a,b in pairs),
            'block_log_ratios':blocks}
        kept=[v for i,v in enumerate(blocks) if i not in varying_blocks]
        rng=random.Random(261021)
        sensitivity=sorted(statistics.mean(rng.choices(kept,k=len(kept))) for _ in range(20000))
        kept_pairs=[pair for i,pair in enumerate(pairs) if i//2 not in varying_blocks]
        result['equal_update_sensitivity']['endpoints'][phase+'/'+metric]={
            'reduction':1-math.exp(statistics.mean(kept)),
            'ci_low':1-math.exp(quantile(sensitivity,.975)),
            'ci_high':1-math.exp(quantile(sensitivity,.025)),
            'paired_saving_median_ns':statistics.median(a-b for a,b in kept_pairs)}
(H/'fill-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
