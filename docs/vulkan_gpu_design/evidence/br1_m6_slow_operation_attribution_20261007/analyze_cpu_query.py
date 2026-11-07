from pathlib import Path
import collections,json,statistics
H=Path(__file__).resolve().parent;O=H/'cpu-query-diagnostic'
rows=json.loads((O/'runs.json').read_text());results=[]
for row in rows:
 data=json.loads(next(t[7:] for t in (O/row['log']).read_text().splitlines() if t.startswith('WINDOW ')))
 assert not data['switch_loaded'] and not data['paired']
 a=data['arms'][0];ns=a['operation_ns'];cores=a['cpu_queries'];n=len(ns)
 assert n==a['completed']==len(cores) and sum(ns)==a['wall_ns'] and sum(ns)>=512000000 and n>=512
 assert a['handoffs']==(n*row['K'] if row['case']=='hit' else 0)
 assert a['copy_bytes']==(0 if row['case']=='hit' else n*row['K']*16384)
 groups={'same_query_0_5':[],'same_query_6_9':[],'different_endpoint_query':[]}
 for w,c in zip(ns,cores):
  assert 0<=c[0]<10 and 0<=c[1]<10
  name='different_endpoint_query' if c[0]!=c[1] else 'same_query_0_5' if c[0]<6 else 'same_query_6_9'
  groups[name].append(w)
 r={k:row[k] for k in ['arch','K','case','repeat','log']}
 r.update(completed=n,wall_ns=sum(ns),median_ns=statistics.median(ns),maximum_ns=max(ns),
  slow_1ms_count=sum(w>=1000000 for w in ns),
  groups={k:{'count':len(v),'wall_ns':sum(v),'median_ns':statistics.median(v) if v else None} for k,v in groups.items()})
 lo,hi=r['groups']['same_query_0_5'],r['groups']['same_query_6_9']
 r['same_query_slow_fast_median_ratio']=lo['median_ns']/hi['median_ns'] if lo['count'] and hi['count'] else None
 results.append(r)
assert len(results)==32
(H/'cpu-query-summary.json').write_text(json.dumps({'processes':results,
 'scope':'Exploratory query strata; no samples deleted, normalized, or qualified; same endpoint does not exclude intervening migration.',
 'verified':True},indent=2)+'\n')
for r in results:print(json.dumps(r))
