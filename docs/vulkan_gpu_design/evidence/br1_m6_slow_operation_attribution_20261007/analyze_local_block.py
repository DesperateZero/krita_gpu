from pathlib import Path
import hashlib,json,math,random,statistics
H=Path(__file__).resolve().parent;O=H/'local-block';runs=json.loads((O/'runs.json').read_text())
assert len(runs)==192 and json.loads((O/'identity-final.json').read_text())['verified']
groups=sorted({(r['arch'],r['K'],r['case'],r['cell']) for r in runs});out=[]
for group in groups:
 for policy in ['global','local']:
  g=[r for r in runs if (r['arch'],r['K'],r['case'],r['cell'])==group and r['policy']==policy]
  logs=[];units=[];gaps=[]
  for block in range(6):
   pairlogs=[];starts=[];ends=[]
   for pair in range(2):
    d={r['arm']:r for r in g if r['block']==block and r['pair']==pair};assert len(d)==2
    a,b=d[0]['observation'],d[1]['observation']
    pairlogs.append(math.log(b['throughput']/a['throughput']))
    starts.append(min(d[a]['start_monotonic'] for a in [0,1]))
    ends.append(max(d[a]['start_monotonic']+d[a]['seconds'] for a in [0,1]))
   logs.extend(pairlogs);units.append(statistics.mean(pairlogs));gaps.append(starts[1]-ends[0])
  rng=random.Random(261015)
  boot=sorted(statistics.median(rng.choices(units,k=len(units))) for _ in range(20000))
  lower,upper=math.exp(boot[500]),math.exp(boot[19500])
  out.append(dict(arch=group[0],K=group[1],case=group[2],cell=group[3],policy=policy,
   processes=len(g),pairs=12,blocks=6,throughput_ratio=math.exp(statistics.median(units)),
   diagnostic_95pct_interval=[lower,upper],descriptively_inside_2pct=lower>=.98 and upper<=1.02,
   paired_log_throughput_sd=statistics.stdev(logs),balanced_log_units=units,
   between_opposite_pair_gap_seconds=gaps,median_gap_seconds=statistics.median(gaps),
   completed=sum(r['observation']['completed'] for r in g),
   wall_ns=sum(r['observation']['wall_ns'] for r in g)))
comparison=[]
for group in groups:
 g,l=[next(r for r in out if (r['arch'],r['K'],r['case'],r['cell'])==group and r['policy']==policy)
      for policy in ['global','local']]
 comparison.append(dict(arch=group[0],K=group[1],case=group[2],cell=group[3],
  paired_log_sd_relative_change=l['paired_log_throughput_sd']/g['paired_log_throughput_sd']-1,
  global_inside=g['descriptively_inside_2pct'],local_inside=l['descriptively_inside_2pct']))
result=dict(rows=out,comparison=comparison,processes=192,
 completed=sum(r['completed'] for r in out),wall_ns=sum(r['wall_ns'] for r in out),
 qualification='Fixed192-process pilot only, unadjusted two-sided95pct; no formal family or production speed qualification',
 protocol_sha256=hashlib.sha256((H/'local-block-PLAN.md').read_bytes()).hexdigest())
(H/'local-block-summary.json').write_text(json.dumps(result,indent=2)+'\n')
for r in out:print(r['arch'],r['K'],r['case'],r['cell'],r['policy'],r['throughput_ratio'],r['diagnostic_95pct_interval'],r['paired_log_throughput_sd'])
