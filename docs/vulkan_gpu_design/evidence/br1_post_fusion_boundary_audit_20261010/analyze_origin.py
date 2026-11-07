#!/usr/bin/env python3
"""Join queue requests to merge executions by pointer AND creation lifetime."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
rows=json.loads((H/'queue-origin/results.json').read_text());assert len(rows)==4 and all(r['passed'] for r in rows)
def area(r):return r[2]*r[3]
def intersect(a,b):
 x=max(a[0],b[0]);y=max(a[1],b[1]);return (x,y,max(0,min(a[0]+a[2],b[0]+b[2])-x),max(0,min(a[1]+a[3],b[1]+b[3])-y))
def union_area(rs):
 ys=sorted({y for r in rs for y in [r[1],r[1]+r[3]]});total=0
 for y,z in zip(ys,ys[1:]):
  end=-10**12
  for a,b in sorted((r[0],r[0]+r[2]) for r in rs if r[1]<=y and r[1]+r[3]>=z):total+=max(0,b-max(a,end))*(z-y);end=max(end,b)
 return total
result=[]
for row in rows:
 es=[e for e in row['events'] if e['stage']==2];by={e['id']:e for e in es}
 def chain(e):
  c=[]
  while e:c.append(e);e=by.get(e['parent'])
  return c
 adds=sorted([e for e in es if e['name']=='queue_add' and not any(a['name']=='queue_add' for a in chain(e)[1:])],key=lambda x:x['start_ns'])
 batches=[]
 for e in adds:
  rects=[x['tags'][:4] for x in es if x['parent']==e['id'] and x['name']=='queue_rect']
  assert len(rects)==e['tags'][1]
  assert sum(area(r) for r in rects)==union_area(rects) # incoming list is disjoint
  batches.append(dict(event=e['id'],inputs=rects,input_area=sum(area(r) for r in rects),merges=[],collections=[]))
 for e in sorted([e for e in es if e['name']=='proj_merge'],key=lambda x:x['start_ns']):
  ptr=e['tags'][0]
  creates=[x for x in es if x['name']=='queue_created' and x['tags'][0]==ptr and x['end_ns']<=e['start_ns']]
  assert creates
  creation=max(creates,key=lambda x:x['start_ns'])
  parent_add=[a for a in chain(creation) if a['name']=='queue_add'][-1]
  batch=next(b for b in batches if b['event']==parent_add['id'])
  cs=[x for x in es if x['name']=='queue_collect' and x['tags'][0]==ptr and creation['start_ns']<=x['start_ns'] and x['end_ns']<=e['start_ns']]
  reads=[x['tags'][:8] for x in es if x['name']=='capture' and e in chain(x)]
  batch['merges'].append(dict(walker=ptr,created_rect=creation['tags'][1:5],executed_rect=e['tags'][1:5],source_captures=reads,collections=[x['tags'][1:6] for x in cs]))
 for b in batches:
  rs=[m['executed_rect'] for m in b['merges']]
  b['executed_area']=sum(area(r) for r in rs);b['executed_union_area']=union_area(rs)
  b['overlapping_revisits']=b['executed_area']-b['executed_union_area'];b['hull_gap_pixels']=b['executed_union_area']-b['input_area']
  # Constructive geometry-only alternative: coalesce exact vertical neighbors of equal x/width.
  merged=[]
  for r in sorted(b['inputs'],key=lambda r:(r[0],r[2],r[1])):
   if merged and merged[-1][0]==r[0] and merged[-1][2]==r[2] and merged[-1][1]+merged[-1][3]==r[1]: merged[-1][3]+=r[3]
   else:merged.append(list(r))
  assert sum(area(r) for r in merged)==b['input_area']
  def pages(r):return ((r[0]+r[2]-1)//64-r[0]//64+1)*((r[1]+r[3]-1)//64-r[1]//64+1)
  b['vertical_exact_alternative']={'rects':merged,'jobs':len(merged),'page_visits':sum(pages(r) for r in merged)}
 result.append({'index':row['index'],'side':row['side'],'batches':batches,'input_rects':sum(len(b['inputs']) for b in batches),'merge_jobs':sum(len(b['merges']) for b in batches),'input_area':sum(b['input_area'] for b in batches),'executed_area':sum(b['executed_area'] for b in batches),'overlapping_revisits':sum(b['overlapping_revisits'] for b in batches),'hull_gap_pixels':sum(b['hull_gap_pixels'] for b in batches),'geometry_alternative_jobs':sum(b['vertical_exact_alternative']['jobs'] for b in batches),'geometry_alternative_page_visits':sum(b['vertical_exact_alternative']['page_visits'] for b in batches)})
(H/'origin-summary.json').write_text(json.dumps(result,indent=2)+'\n')
for r in result:print({k:v for k,v in r.items() if k!='batches'})
