#!/usr/bin/env python3
import argparse,json,random,statistics
from pathlib import Path
H=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('batch');a=p.parse_args();rows=json.loads((H/a.batch/'results.json').read_text());assert all(r['passed'] for r in rows)
blocks=sorted({r['block'] for r in rows});pair=['candidate','upstream'] if a.batch.startswith('upstream') else ['parent','candidate']
bootstrap=not a.batch.startswith('explore');rng=random.Random(20261010);indices=[rng.choices(blocks,k=len(blocks)) for _ in range(100000)] if bootstrap else []
def calc(fn,ratio=False):
 values=[]
 for b in blocks:
  means=[statistics.mean(fn(r) for r in rows if r['side']==s and r['block']==b) for s in pair]
  values.append(means[0]/means[1] if ratio else means[0]-means[1])
 out={'median':statistics.median(values),'blocks':values}
 if bootstrap:
  dist=sorted(statistics.median(values[i] for i in ix) for ix in indices);out['ci95_pointwise']=[dist[2499],dist[97499]]
 return out
out={'batch':a.batch,'processes':len(rows),'independent_blocks':len(blocks),'difference':pair[0]+' minus '+pair[1]}
if rows[0]['work']=='storage':
 out['cases']={}
 for i in range(8):
  def c(r):return next(x for x in r['cases'] if x['case']==i)
  v={k:c(rows[0])[k] for k in ['pages','writes','history','lifetimes']}
  for metric in ['cpu_ns','wall_ns']:
   v[metric]={phase:calc(lambda r:c(r)[phase][metric]/1e6) for phase in ['setup','write','read','finish','undo','redo','teardown']}
   v[metric]['case']=calc(lambda r:c(r)['case_'+metric]/1e6)
  v['write_ratio']=calc(lambda r:c(r)['write']['cpu_ns'],True)
  out['cases'][str(i)]=v
  print(i,'write',v['cpu_ns']['write'],'case',v['cpu_ns']['case'],flush=True)
else:
 out['stages']={s:{metric:calc(lambda r:next(t for t in r['stages'] if t['stage']==s)[metric]/1e6) for metric in ['cpu_ns','wall_ns']} for s in ['Setup','Stroke','Undo','Redo','Teardown']}
 print(out['stages'])
(H/(a.batch+'-summary.json')).write_text(json.dumps(out,indent=2)+'\n')
