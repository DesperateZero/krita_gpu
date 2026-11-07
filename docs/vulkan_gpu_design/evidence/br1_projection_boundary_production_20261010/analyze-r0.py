#!/usr/bin/env python3
import hashlib,json,random,statistics
from pathlib import Path
H=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def bootstrap(values):
 rng=random.Random(20261010);n=len(values)
 samples=sorted(statistics.median(rng.choices(values,k=n)) for _ in range(50000))
 return [samples[int(.025*(len(samples)-1))],samples[int(.975*(len(samples)-1))]]
rows=json.loads((H/'confirm/results.json').read_text());assert len(rows)==64 and all(r['passed'] for r in rows)
results=[]
for stage in ['Setup','Stroke','Undo','Redo','Teardown']:
 for metric in ['cpu_ns','wall_ns']:
  deltas=[];relatives=[];parent=[];candidate=[]
  for b in range(16):
   block=rows[4*b:4*b+4];assert all(sum(r['configuration']==c for r in block)==2 for c in ['parent','candidate'])
   values={c:statistics.mean(next(s[metric] for s in r['stages'] if s['stage']==stage) for r in block if r['configuration']==c)/1e6 for c in ['parent','candidate']}
   deltas.append(values['parent']-values['candidate']);relatives.append(100*deltas[-1]/values['parent']);parent.append(values['parent']);candidate.append(values['candidate'])
  results.append(dict(stage=stage,metric=metric,block_savings_ms=deltas,median_block_saving_ms=statistics.median(deltas),median_block_relative_saving_percent=statistics.median(relatives),median_parent_block_mean_ms=statistics.median(parent),median_candidate_block_mean_ms=statistics.median(candidate),pointwise_95_ci_ms=bootstrap(deltas)))
primary=next(r for r in results if r['stage']=='Stroke' and r['metric']=='cpu_ns')
mechanisms=[]
names=['merge','fusion_attempts','unused','fused_clear','failed_fusion','initialized_bytes','pixel_operations','fill_operations','accepted_cold_plans','new_batches','successful_seals','commits']
for r in json.loads((H/'capability/results.json').read_text()):
 assert r['passed']
 for c in r['counts']:mechanisms.append(dict(index=r['index'],configuration=r['configuration'],stage=c['stage'],**dict(zip(names,c['values']))))
# Verify same actual workspace runtime dependencies apart from image library.
runtimes=[]
for r in rows:
 loaded=json.loads((H/'confirm'/f"{r['index']:02}-{r['configuration']}"/'runtime.json').read_text())
 runtimes.append({p:v for p,v in loaded.items() if 'libkritaimage.' not in p})
assert all(x==runtimes[0] for x in runtimes)
result=dict(performance=results,mechanisms=mechanisms,incremental_value_passed=primary['median_block_saving_ms']>=.5 and primary['pointwise_95_ci_ms'][0]>0,prediction={'engineering_range_ms':[.5,1.5],'within_range':.5<=primary['median_block_saving_ms']<=1.5,'prior_prototype_ms':1.05775,'difference_from_prior_prototype_ms':primary['median_block_saving_ms']-1.05775},same_runtime_dependencies=True,inputs={str(p):sha(p) for p in [H/'PROTOCOL.md',H/'PRE_CONFIRMATION.md',H/'confirm/results.json',H/'capability/results.json',Path(__file__)]},limits='Pointwise intervals only; independent production increment, no upstream/GPU/formal M6 qualification.')
(H/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
