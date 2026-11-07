#!/usr/bin/env python3
"""Predeclared block comparisons and nested diagnostic accounting, no exclusions."""
import argparse,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--revision',default='');a=p.parse_args()
prefix=a.revision+'-' if a.revision else ''
def quantile(v,q):
    p=(len(v)-1)*q;i=int(p);return v[i]+(v[min(i+1,len(v)-1)]-v[i])*(p-i)
for batch in ['parent','upstream']:
    path=H/('runs-'+prefix+batch)/'results.json'
    if not path.exists():continue
    rows=json.loads(path.read_text());assert len(rows)==80 and all(r['passed'] for r in rows)
    result=dict(blocks=20,bootstrap=20000,seed=261021,interval='pointwise two-sided95%; no formal family qualification',endpoints={},
        workload_variations=[dict(index=r['index'],side=r['side'],updates=r['sample']['projection_updates']) for r in rows if r['sample']['projection_updates']!=19])
    for phase in ['Stroke','Undo','Redo','Teardown']:
        for metric in ['wall_ns','cpu_ns']:
            pairs=[]
            for i in range(0,80,2):
                p={r['side']:next(s[metric] for s in r['stages'] if s['stage']==phase) for r in rows[i:i+2]};pairs.append((p[batch],p['candidate']))
            logs=[math.log(b/a) for a,b in pairs];blocks=[statistics.mean(logs[i:i+2]) for i in range(0,40,2)]
            rng=random.Random(261021);resamples=sorted(statistics.mean(rng.choices(blocks,k=20)) for _ in range(20000))
            lo,hi=math.exp(quantile(resamples,.025)),math.exp(quantile(resamples,.975))
            result['endpoints'][phase+'/'+metric]=dict(candidate_over_baseline=math.exp(statistics.mean(blocks)),ratio_ci=[lo,hi],
                reduction=1-math.exp(statistics.mean(blocks)),reduction_ci=[1-hi,1-lo],
                baseline_median_ns=statistics.median(a for a,b in pairs),candidate_median_ns=statistics.median(b for a,b in pairs),
                paired_saving_median_ns=statistics.median(a-b for a,b in pairs),control_pass=hi<=1.02,blocks=blocks)
    (H/(prefix+batch+'-summary.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(batch)
    for n,v in result['endpoints'].items():print(n,round(100*v['reduction'],2),[round(100*x,2) for x in v['reduction_ci']],round(v['paired_saving_median_ns']/1e6,3))
for batch in ['diagnostic','outer']:
    path=H/('runs-'+prefix+batch)/'results.json'
    if not path.exists():continue
    rows=json.loads(path.read_text());assert len(rows)==10 and all(r['passed'] for r in rows)
    summary=[]
    for r in rows:
        events={e['id']:e for e in r['events']}
        def in_projection(e):
            while e:
                if e['name']=='proj_merge':return True
                e=events.get(e['parent'])
            return False
        names=defaultdict(lambda:dict(count=0,cpu_ns=0,self_cpu_ns=0))
        for e in events.values():
            if e['stage']!=2 or e['end_stage']!=2 or not in_projection(e):continue
            n=names[e['name']];n['count']+=1;n['cpu_ns']+=e['cpu_ns'];n['self_cpu_ns']+=e['self_cpu_ns']
        stroke=Counter(e['name'] for e in events.values() if e['stage']==2 and e['end_stage']==2)
        summary.append(dict(index=r['index'],side=r['side'],projection=dict(names),stroke_counts=dict(stroke),updates=r['sample']['projection_updates']))
    (H/(prefix+batch+'-summary.json')).write_text(json.dumps(summary,indent=2)+'\n')
    for side in ['parent','candidate','upstream']:
        subset=[r for r in summary if r['side']==side];print(batch,side,'projection ms',[round(r['projection']['proj_merge']['cpu_ns']/1e6,3) for r in subset])

if not (H/(prefix+'diagnostic-summary.json')).exists():raise SystemExit(0)
detail=json.loads((H/(prefix+'diagnostic-summary.json')).read_text());mechanism={}
for side in ['parent','candidate']:
    rows=[r for r in detail if r['side']==side];mechanism[side]={}
    for name in ['fill','completion_allocate','completion_complete','physical_record','private_prepare','private_publish','cold','overlay_input','seal','commit','capture','operation','proj_merge']:
        values=[r['projection'].get(name,dict(count=0,cpu_ns=0,self_cpu_ns=0)) for r in rows]
        mechanism[side][name]=dict(counts=sorted(set(v['count'] for v in values)),cpu_median_ms=statistics.median(v['cpu_ns'] for v in values)/1e6,self_median_ms=statistics.median(v['self_cpu_ns'] for v in values)/1e6)
outer=json.loads((H/(prefix+'outer-summary.json')).read_text())
med={side:statistics.median(r['projection']['proj_merge']['cpu_ns']/1e6 for r in outer if r['side']==side) for side in ['parent','candidate','upstream']}
savings=[]
for i in range(0,8,2):
    pair={r['side']:r['projection']['proj_merge']['cpu_ns']/1e6 for r in outer[i:i+2]};savings.append(pair['parent']-pair['candidate'])
mechanism['outer']=dict(parent_median_ms=med['parent'],candidate_median_ms=med['candidate'],upstream_median_ms=med['upstream'],paired_saving_ms=savings,paired_saving_median_ms=statistics.median(savings),residual_ms=med['candidate']-med['upstream'],descriptive_gap_closed=(med['parent']-med['candidate'])/(med['parent']-med['upstream']))
(H/(prefix+'mechanism-summary.json')).write_text(json.dumps(mechanism,indent=2)+'\n')
