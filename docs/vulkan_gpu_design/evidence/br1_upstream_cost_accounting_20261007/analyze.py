#!/usr/bin/env python3
"""Process CPU and nested observed costs; never add inclusive parents to children."""
import json,statistics
from collections import defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
median=statistics.median
def describe(values):return {'median':median(values),'min':min(values),'max':max(values),'n':len(values)}
baseline=load(H/'baseline/results.json');assert len(baseline)==16 and all(r['passed'] for r in baseline)
result={'baseline':{},'interpretation':'ARM native fixed eight pairs. Descriptive statistics only, no formal gate or gain claim. Process CPU includes all process threads; self wall is additive only on one thread. Non-CPU interval is not identified lock wait. Instrumented values are not unmodified product prices.'}
for phase in ['Setup','Stroke','Undo','Redo','Teardown']:
    metrics=['wall_ns','cpu_ns','user_ns','system_ns']
    rows=[dict(side=r['side'],**next(x for x in r['stages'] if x['stage']==phase)) for r in baseline]
    paired=[]
    for i in range(0,16,2):
        a,b=sorted(rows[i:i+2],key=lambda x:x['side'])
        assert a['side']=='current' and b['side']=='upstream'
        paired.append({k:{'delta':a[k]-b[k],'ratio':a[k]/b[k] if b[k] else None} for k in metrics})
    result['baseline'][phase]={'sides':{s:{k:describe([r[k] for r in rows if r['side']==s]) for k in metrics} for s in ['current','upstream']},
        'paired':{k:{'delta':describe([r[k]['delta'] for r in paired]),'ratio':describe([r[k]['ratio'] for r in paired if r[k]['ratio'] is not None])} for k in metrics},
        'cpu_per_wall':{s:describe([r['cpu_ns']/r['wall_ns'] for r in rows if r['side']==s]) for s in ['current','upstream']}}
def union_ns(intervals):
    end=None;total=0
    for a,b in sorted(intervals):
        if end is None or a>=end:total+=b-a;end=b
        elif b>end:total+=b-end;end=b
    return total
def analyze_observed(row):
    events=row['events'];byid={e['id']:e for e in events};assert len(byid)==len(events)
    children=defaultdict(list)
    for e in events:
        if e['parent']:
            assert e['parent'] in byid
            p=byid[e['parent']]
            assert e['thread']==p['thread'] and p['start_ns']<=e['start_ns']<=e['end_ns']<=p['end_ns']
            children[e['parent']].append(e)
    for e in events:
        cs=children[e['id']]
        assert e['self_cpu_ns']+sum(c['cpu_ns'] for c in cs)==e['cpu_ns']
        assert e['self_wall_ns']+sum(c['end_ns']-c['start_ns'] for c in cs)==e['end_ns']-e['start_ns']
    out={'side':row['side'],'mode':row['mode'],'index':row['index'],'checks':row['checks'],'stages':{}}
    for i,s in enumerate(row['stages'],1):
        chosen=[e for e in events if e['stage']==i and e['start_ns']>=s['start_ns'] and e['end_ns']<=s['end_ns']]
        crossing=[e for e in events if e['stage']==i and e not in chosen]
        names=defaultdict(lambda:dict(calls=0,cpu_ns=0,self_cpu_ns=0,wall_ns=0,self_wall_ns=0))
        actors=defaultdict(lambda:defaultdict(lambda:dict(calls=0,cpu_ns=0,self_cpu_ns=0)))
        for e in chosen:
            n=names[e['name']];n['calls']+=1
            for k in ['cpu_ns','self_cpu_ns','self_wall_ns']:n[k]+=e[k]
            n['wall_ns']+=e['end_ns']-e['start_ns']
            top=e
            while top['parent']:top=byid[top['parent']]
            a=actors[top['name']][e['name']];a['calls']+=1;a['cpu_ns']+=e['cpu_ns'];a['self_cpu_ns']+=e['self_cpu_ns']
        jobs=[e for e in chosen if e['name'] in ['job_stroke','job_merge','job_spontaneous']]
        out['stages'][s['stage']]={'process':s,'names':dict(sorted(names.items(),key=lambda x:x[1]['self_cpu_ns'],reverse=True)),
            'observed_exclusive_cpu_ns':sum(e['self_cpu_ns'] for e in chosen),
            'unassigned_cpu_ns':s['cpu_ns']-sum(e['self_cpu_ns'] for e in chosen),
            'job_union_wall_ns':union_ns([(e['start_ns'],e['end_ns']) for e in jobs]),
            'job_summed_wall_ns':sum(e['end_ns']-e['start_ns'] for e in jobs),
            'job_inclusive_cpu_ns':sum(e['cpu_ns'] for e in jobs),
            'job_non_cpu_ns':sum((e['end_ns']-e['start_ns'])-e['cpu_ns'] for e in jobs),
            'cross_boundary_events':len(crossing),'complete_events':len(chosen),'actors':{k:dict(v) for k,v in actors.items()}}
    return out
if (H/'diagnostic/results.json').exists():
    rows=load(H/'diagnostic/results.json');assert len(rows)==12 and all(r['passed'] for r in rows)
    observed=[analyze_observed(r) for r in rows]
    result['observed']=observed
    result['observer_perturbation']={}
    for side in ['current','upstream']:
        values={mode:[r['stages']['Stroke']['process'] for r in observed if r['side']==side and r['mode']==mode] for mode in [0,1,2]}
        result['observer_perturbation'][side]={mode:{k:describe([v[k] for v in samples]) for k in ['wall_ns','cpu_ns']} for mode,samples in values.items()}
if (H/'payload/results.json').exists():
    rows=load(H/'payload/results.json');assert len(rows)==4 and all(r['passed'] for r in rows)
    result['payload_observed']=[analyze_observed(r) for r in rows]
(H/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['baseline']['Stroke'],indent=2))
if 'observed' in result:
    for r in result['observed']:
        s=r['stages']['Stroke'];print(json.dumps(dict(side=r['side'],mode=r['mode'],index=r['index'],process_cpu_ms=s['process']['cpu_ns']/1e6,wall_ms=s['process']['wall_ns']/1e6,observed_cpu_ms=s['observed_exclusive_cpu_ns']/1e6,top=[(n,round(v['self_cpu_ns']/1e6,3),v['calls']) for n,v in list(s['names'].items())[:15]])))
