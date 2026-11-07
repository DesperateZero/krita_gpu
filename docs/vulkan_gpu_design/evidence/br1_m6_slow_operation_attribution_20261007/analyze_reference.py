from pathlib import Path
import collections,json,math,statistics
H=Path(__file__).resolve().parent;O=H/'reference-diagnostic'
rows=json.loads((O/'runs.json').read_text());results=[]
def corr(xs,ys):
 ax,ay=statistics.mean(xs),statistics.mean(ys)
 num=sum((x-ax)*(y-ay) for x,y in zip(xs,ys))
 den=math.sqrt(sum((x-ax)**2 for x in xs)*sum((y-ay)**2 for y in ys))
 return num/den if den else None
for row in rows:
 a=json.loads(next(t[7:] for t in (O/row['log']).read_text().splitlines() if t.startswith('WINDOW ')))['arms'][0]
 ns=a['operation_ns'];refs=a['reference'];cpu=a['cpu_ns'];n=len(ns);m=statistics.median(ns)
 assert n==a['completed']==len(refs)==len(cpu) and sum(ns)==a['wall_ns'] and sum(ns)>=512000000
 assert a['handoffs']==(n if row['case']=='hit' else 0) and a['copy_bytes']==(0 if row['case']=='hit' else n*16384)
 rs=[(r[2]+r[6])/2 for r in refs]
 cores=collections.defaultdict(list);slow=[];typical=[]
 for i,(w,r) in enumerate(zip(ns,refs)):
  if r[0]==r[1]:cores[r[0]].append((w,rs[i]))
  (slow if w>=2*m else typical).append(i)
 bycore={str(k):{'count':len(v),'product_median_ns':statistics.median(x[0] for x in v),
  'reference_median_ns':statistics.median(x[1] for x in v)} for k,v in cores.items()}
 result={k:row[k] for k in ['arch','K','case','repeat','log']}
 result.update(completed=n,wall_ns=sum(ns),median_ns=m,reference_median_ns=statistics.median(rs),
  pearson_product_reference=corr(ns,rs),slow_2x_median_count=len(slow),
  slow_reference_median_ns=statistics.median(rs[i] for i in slow) if slow else None,
  typical_reference_median_ns=statistics.median(rs[i] for i in typical),
  operation_endpoint_migrations=sum(r[0]!=r[1] for r in refs),
  reference_endpoint_migrations=sum(r[4]!=r[5] or r[8]!=r[9] for r in refs),by_query_cpu=bycore)
 results.append(result)
assert len(results)==16
(H/'reference-summary.json').write_text(json.dumps({'processes':results,
 'scope':'Fixed reference is observational; changes environment and cannot normalize original performance. CPU ids are query snapshots, not residency proof or core type.',
 'verified':True},indent=2)+'\n')
for r in results:print(json.dumps(r))
