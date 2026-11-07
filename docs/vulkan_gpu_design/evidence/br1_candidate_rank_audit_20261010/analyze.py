#!/usr/bin/env python3
"""D1: checked exclusive event accounting, paired mode effects, no inferred CI."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import statistics

H=Path(__file__).resolve().parent
rows=json.loads((H/'matrix/results.json').read_text())
assert len(rows)==16 and all(r['passed'] for r in rows)
def stats(v):return dict(values=v,mean=statistics.mean(v),median=statistics.median(v),minimum=min(v),maximum=max(v))
processes=[]
for row in rows:
    all_events=row['events']
    byid={e['id']:e for e in all_events};children=defaultdict(list)
    for e in all_events:
        if e['parent']:
            assert e['parent'] in byid and byid[e['parent']]['thread']==e['thread']
            children[e['parent']].append(e)
    for e in all_events:
        assert e['cpu_ns']==e['self_cpu_ns']+sum(c['cpu_ns'] for c in children[e['id']])
        assert e['end_ns']-e['start_ns']==e['self_wall_ns']+sum(c['end_ns']-c['start_ns'] for c in children[e['id']])
    events=[e for e in all_events if e['stage']==2]
    buckets=defaultdict(float);inclusive=defaultdict(float);counts=defaultdict(int)
    closed=defaultdict(float);crossing=defaultdict(float);history={}
    for e in events:
        chain=[];at=e
        while at:
            assert at['id'] not in chain
            chain.append(at['id']);at=byid.get(at['parent'])
        context='projection' if any(byid[i]['name']=='proj_merge' for i in chain) else 'other'
        name=context+'/'+e['name']
        buckets[name]+=e['self_cpu_ns']/1e6;inclusive[name]+=e['cpu_ns']/1e6;counts[name]+=1
        destination=closed if e['end_stage']==2 else crossing
        destination[name]+=e['self_cpu_ns']/1e6
    stage=next(s for s in row['stages'] if s['stage']=='Stroke')
    observed=sum(e['cpu_ns'] for e in events if not e['parent'])/1e6
    assert abs(observed-sum(buckets.values()))<1e-8
    for name in ['history_job','history_pass']:
        es=[e for e in events if e['name']==name]
        history[name]=dict(closed_inclusive_ms=sum(e['cpu_ns'] for e in es if e['end_stage']==2)/1e6,
                          crossing_inclusive_ms=sum(e['cpu_ns'] for e in es if e['end_stage']!=2)/1e6,
                          started_calls=len(es),closed_calls=sum(e['end_stage']==2 for e in es))
    assert sum(closed.values())<=stage['cpu_ns']/1e6
    processes.append(dict(index=row['index'],block=row['block'],configuration=row['configuration'],
                          stroke_cpu_ms=stage['cpu_ns']/1e6,stroke_wall_ms=stage['wall_ns']/1e6,
                          inclusive_ms=dict(inclusive),exclusive_ms=dict(buckets),counts=dict(counts),
                          uncovered_cpu_ms=stage['cpu_ns']/1e6-sum(closed.values()),
                          closed_exclusive_ms=dict(closed),crossing_exclusive_ms=dict(crossing),history=history,
                          updates=row['sample']['projection_updates'],amounts=row['amounts']))
modes={}
for mode in ['raw','off','coarse','history']:
    selected=[r for r in processes if r['configuration']==mode]
    result={name:stats([r[name] for r in selected]) for name in ['stroke_cpu_ms','stroke_wall_ms','uncovered_cpu_ms']}
    for field in ['inclusive_ms','exclusive_ms','counts']:
        result[field]={key:stats([r[field].get(key,0) for r in selected]) for key in sorted({k for r in selected for k in r[field]})}
    modes[mode]=result
changes=[]
for before,after in [('raw','off'),('off','coarse'),('coarse','history')]:
    changes.append(dict(before=before,after=after,paired_cpu_ms=stats([
        next(r['stroke_cpu_ms'] for r in processes if r['configuration']==after and r['block']==b)-
        next(r['stroke_cpu_ms'] for r in processes if r['configuration']==before and r['block']==b) for b in range(4)])))
outer=modes['coarse'];facts=modes['history']
proj=lambda m:m['inclusive_ms']['projection/proj_merge']['median']
perturbation=dict(projection_cpu_ratio=proj(facts)/proj(outer),stroke_cpu_median_increase_ms=facts['stroke_cpu_ms']['median']-outer['stroke_cpu_ms']['median'])
perturbation['history_price_restricted']=perturbation['projection_cpu_ratio']>1.15 or perturbation['stroke_cpu_median_increase_ms']>.25
result=dict(method='fixed 4-process/config descriptive evidence, no new CI; inclusive not additive; started scopes include crossing tails, closed/crossing accounting separate; scopes started outside observed stages may be unrecorded',modes=modes,mode_changes=changes,perturbation=perturbation,processes=processes,
            inputs={str(p.relative_to(H)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [H/'PROTOCOL.md',H/'run.py',Path(__file__),H/'matrix/results.json']})
(H/'summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('CPU medians', {m:round(v['stroke_cpu_ms']['median'],4) for m,v in modes.items()})
print('perturbation',perturbation)
for mode in ['coarse','history']:
    print(mode,{k:round(v['median'],6) for k,v in modes[mode]['inclusive_ms'].items()})
