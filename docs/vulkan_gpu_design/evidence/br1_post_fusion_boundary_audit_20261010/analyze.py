#!/usr/bin/env python3
"""Finite paired CPU ledger and projection page lineage; raw samples are immutable."""
import json,statistics,random
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent
med=statistics.median

def summary(v):
    v=list(v); rng=random.Random(20261010)
    b=sorted(med(rng.choices(v,k=len(v))) for _ in range(100000))
    return {'median':med(v),'ci95_pointwise':[b[2499],b[97499]],'blocks':v}

def stage(r,s):return next(x for x in r['stages'] if x['stage']==s)

def paired(rows,fn):
    return [statistics.mean(fn(r) for r in rows if r['block']==b and r['side']=='current')-statistics.mean(fn(r) for r in rows if r['block']==b and r['side']=='upstream') for b in sorted({r['block'] for r in rows})]

allrows={b:json.loads((H/b/'results.json').read_text()) for b in ['capability','original','jobs','off','lineage']}
assert {b:len(r) for b,r in allrows.items()}==dict(capability=8,original=32,jobs=16,off=8,lineage=4)
assert all(r['passed'] for rs in allrows.values() for r in rs)
result={'difference_direction':'current minus upstream, ms; positive is extra cost','processes':68}
result['original']={s:{metric:summary(paired(allrows['original'],lambda r:stage(r,s)[metric]/1e6)) for metric in ['cpu_ns','wall_ns']} for s in ['Stroke','Undo','Redo','Teardown']}
result['marginal']={b:{side:{s:{m:med(stage(r,s)[m]/1e6 for r in rs if r['side']==side) for m in ['cpu_ns','wall_ns']} for s in ['Stroke','Undo','Redo','Teardown']} for side in ['current','upstream']} for b,rs in allrows.items() if b in ['original','jobs','off']}
result['update_counts']={b:dict(Counter((r['side']+':'+str(r['sample']['projection_updates'])) for r in rs)) for b,rs in allrows.items()}

rows=allrows['jobs']
for r in rows:
    events=[e for e in r['events'] if e['stage']==2]
    roots=[e for e in events if not e['parent']]
    assert all(e['name'].startswith('job_') for e in roots)
    c=defaultdict(float)
    for e in roots:c[e['name']]+=e['cpu_ns']/1e6
    c['uncovered']=stage(r,'Stroke')['cpu_ns']/1e6-sum(c.values())
    assert c['uncovered']>=0
    c['projection_inside_merge']=sum(e['cpu_ns']/1e6 for e in events if e['name']=='proj_merge')
    r['coarse']=dict(c)
keys=sorted({k for r in rows for k in r['coarse']})
result['jobs']={'extra_ms':{k:summary(paired(rows,lambda r:r['coarse'].get(k,0))) for k in keys},'marginal_ms':{side:{k:med(r['coarse'].get(k,0) for r in rows if r['side']==side) for k in keys} for side in ['current','upstream']},'per_process':[{k:r[k] for k in ['index','block','side','coarse']} for r in rows]}

def intersect(a,b):
    x=max(a[0],b[0]);y=max(a[1],b[1]); xx=min(a[0]+a[2],b[0]+b[2]); yy=min(a[1]+a[3],b[1]+b[3]);return (x,y,max(0,xx-x),max(0,yy-y))
def area(r):return r[2]*r[3]
def union_area(rects):
    # Integer rectangles; exact scanline union, never pixel output equivalence.
    ys=sorted({v for r in rects for v in [r[1],r[1]+r[3]]})
    total=0
    for a,b in zip(ys,ys[1:]):
        spans=sorted((r[0],r[0]+r[2]) for r in rects if r[1]<=a and r[1]+r[3]>=b)
        end=-10**12
        for x,z in spans:
            total+=max(0,z-max(x,end))*(b-a);end=max(end,z)
    return total

traces=[]
for r in allrows['lineage']:
    events=[e for e in r['events'] if e['stage']==2]; by={e['id']:e for e in events}
    def ancestor(e,name):
        while e:
            if e['name']==name:return e
            e=by.get(e['parent'])
    merges=sorted([e for e in events if e['name']=='proj_merge'],key=lambda e:e['start_ns'])
    ranks={e['id']:i for i,e in enumerate(merges)}
    cold=[e for e in events if e['name']=='cold' and ancestor(e,'proj_merge')]
    counters=Counter();pages=defaultdict(list);generations={};details=[]
    for e in sorted(cold,key=lambda e:e['start_ns']):
        t=e['tags'];assert t[6]>0
        merge=ancestor(e,'proj_merge');comp=ancestor(e,'proj_composite');assert comp
        key=tuple(t[:4]);page=(t[2]*64,t[3]*64,64,64)
        rect=intersect(comp['tags'][:4],page)
        prev=generations.get((key,t[5]))
        row=dict(merge=ranks[merge['id']],key=list(key),base=t[4],source=t[5],target=t[6],transaction=t[7],flags=t[9],rect=list(rect),cpu_ms=e['cpu_ns']/1e6)
        if not pages[key]:kind='first_page'
        elif prev:
            assert prev['merge']!=row['merge']
            kind='prior_generation_disjoint_rect' if not area(intersect(prev['rect'],rect)) else 'prior_generation_overlapping_rect'
            row['previous_merge']=prev['merge'];row['pair_overlap_pixels']=area(intersect(prev['rect'],rect))
        else:kind='repeat_without_traced_source'
        row['kind']=kind;counters[kind]+=1
        generations[(key,t[6])]=row;pages[key].append(row);details.append(row)
    capture=[e for e in events if e['name']=='capture' and ancestor(e,'proj_merge')]
    projection_stores={e['tags'][0] for e in cold}
    merge_rows=[]
    for e in merges:
        inside=[x for x in events if ancestor(x,'proj_merge') is e]
        co=Counter(x['name'] for x in inside)
        source_reads=[x['tags'][:5] for x in inside if x['name']=='capture' and x['tags'][0] not in projection_stores]
        merge_rows.append(dict(index=ranks[e['id']],start_ns=e['start_ns'],end_ns=e['end_ns'],counts=dict(co),rects=[x['tags'][:4] for x in inside if x['name']=='proj_composite'],source_capture_tags=source_reads))
    contexts=defaultdict(lambda:defaultdict(float));counts=defaultdict(Counter)
    for e in events:
        m=ancestor(e,'proj_merge');j=ancestor(e,'job_stroke')
        context='projection' if m else 'stroke' if j else 'other'
        contexts[context][e['name']]+=e['self_cpu_ns']/1e6;counts[context][e['name']]+=1
    traces.append(dict(index=r['index'],cold=len(cold),unique_pages=len(pages),classification=dict(counters),rectangle_visits_pixels=sum(area(d['rect']) for d in details),rectangle_union_pixels=sum(union_area([d['rect'] for d in ds]) for ds in pages.values()),projection_captures=len(capture),capture_kinds=dict(Counter(str(e['tags'][1]) for e in capture)),merges=merge_rows,details=details,observed_exclusive_ms={k:dict(v) for k,v in contexts.items()},counts={k:dict(v) for k,v in counts.items()}))
result['lineage']=traces
(H/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['lineage','jobs','marginal']},indent=2))
print(json.dumps(result['jobs']['extra_ms'],indent=2))
for r in traces: print({k:v for k,v in r.items() if k not in ['merges','details','observed_exclusive_ms','counts']})
