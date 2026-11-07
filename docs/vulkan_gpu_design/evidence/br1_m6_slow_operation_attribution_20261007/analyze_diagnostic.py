from pathlib import Path
import collections,hashlib,json,statistics
H=Path(__file__).resolve().parent;O=H/'diagnostic'
runs=json.loads((O/'runs.json').read_text());clocks=json.loads((O/'clock-validation.json').read_text())
groups=collections.defaultdict(list);events=[];processes=[]
for row in runs:
 if row['kind']!='operation':continue
 raw=(O/row['log']).read_text()
 data=json.loads(next(t[7:] for t in raw.splitlines() if t.startswith('WINDOW ')))
 assert not data['paired'] and not data['switch_loaded'] and len(data['arms'])==1
 a=data['arms'][0];ns=a['operation_ns'];cpu=a['cpu_ns'];ctx=a['operation_context'];n=len(ns)
 assert n==a['completed']==len(cpu)==len(ctx) and sum(ns)==a['wall_ns'] and min(ns)>0
 assert sum(ns)>=128000000 and n>=512
 assert a['handoffs']==(n*row['K'] if row['case']=='hit' else 0)
 assert a['copy_bytes']==(0 if row['case']=='hit' else n*row['K']*16384)
 metric=0 if clocks[row['arch']]['thread']['valid'] else 1
 assert clocks[row['arch']]['thread' if metric==0 else 'process']['valid']
 slow=[];classes=collections.Counter();classwall=collections.Counter()
 for i,(w,c,ct) in enumerate(zip(ns,cpu,ctx)):
  if w<1000000:continue
  fraction=c[metric]/w
  name='cpu_dominant' if fraction>=.8 else 'non_cpu_dominant' if fraction<=.2 else 'mixed'
  e=dict(arch=row['arch'],K=row['K'],case=row['case'],repeat=row['repeat'],index=i,wall_ns=w,
   thread_cpu_ns=c[0],process_cpu_ns=c[1],cpu_fraction=fraction,classification=name,
   minor_faults=ct[0],major_faults=ct[1],voluntary_switches=ct[2],involuntary_switches=ct[3],log=row['log'])
  events.append(e);slow.append(e);classes[name]+=1;classwall[name]+=w
 result=dict(arch=row['arch'],K=row['K'],case=row['case'],repeat=row['repeat'],completed=n,
  wall_ns=sum(ns),median_ns=statistics.median(ns),maximum_ns=max(ns),slow_count=len(slow),
  slow_wall_ns=sum(e['wall_ns'] for e in slow),classes=dict(classes),class_wall_ns=dict(classwall),
  operation_vector_sha256=hashlib.sha256(json.dumps([ns,cpu,ctx]).encode()).hexdigest(),
  context_sums=[sum(c[i] for c in ctx) for i in range(4)],
  clock_metric='thread' if metric==0 else 'process_all_threads')
 groups[(row['arch'],row['K'],row['case'])].append(result);processes.append(result)
summary=[]
for key,rows in groups.items():
 assert len(rows)==4
 n=sum(r['completed'] for r in rows);w=sum(r['wall_ns'] for r in rows)
 es=[e for e in events if (e['arch'],e['K'],e['case'])==key]
 cs=collections.Counter(e['classification'] for e in es)
 cw={c:sum(e['wall_ns'] for e in es if e['classification']==c) for c in cs}
 summary.append(dict(arch=key[0],K=key[1],case=key[2],completed=n,wall_ns=w,
  process_medians_ns=[r['median_ns'] for r in rows],maximum_ns=max(r['maximum_ns'] for r in rows),
  slow_count=len(es),slow_wall_fraction=sum(e['wall_ns'] for e in es)/w,
  slow_classes=dict(cs),slow_class_wall_ns=cw,
  slow_with_major_faults=sum(e['major_faults']>0 for e in es),
  slow_with_minor_faults=sum(e['minor_faults']>0 for e in es),
  slow_with_voluntary_switches=sum(e['voluntary_switches']>0 for e in es),
  slow_with_involuntary_switches=sum(e['involuntary_switches']>0 for e in es)))
assert len(processes)==32 and len(summary)==8
out={'clock_validation':clocks,'processes':processes,'buckets':summary,'slow_events':events,
 'statistical_scope':'32 diagnostic processes; internal operations dependent, no CI or gate qualification',
 'instrumentation_scope':'CPU span includes timer/rusage calls outside original wall interval; no subtraction; slow threshold >=1ms only',
 'verified':True}
(H/'diagnostic-summary.json').write_text(json.dumps(out,indent=2)+'\n')
for s in summary:print(json.dumps(s))
