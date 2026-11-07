#!/usr/bin/env python3
import hashlib,json,math,random,statistics
from pathlib import Path
H=Path(__file__).resolve().parent;median=statistics.median
load=lambda name:json.loads((H/name).read_text())
result={'analysis_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
def estimate(rows,pairs,endpoint,seed):
 logs=[];saving=[];values={'parent':[],'candidate':[]}
 for pair in range(pairs):
  group={r['side']:r['sample'][endpoint] for r in rows if r['pair']==pair}
  assert set(group)=={'parent','candidate'} and min(group.values())>0
  logs.append(math.log(group['candidate']/group['parent']));saving.append(group['parent']-group['candidate'])
  for side,value in group.items():values[side].append(value)
 blocks=[(logs[i]+logs[i+1])/2 for i in range(0,pairs,2)]
 rng=random.Random(seed);boot=sorted(median(rng.choices(blocks,k=len(blocks))) for _ in range(20000))
 point=math.exp(median(blocks));lo=math.exp(boot[500]);hi=math.exp(boot[19500])
 return dict(pairs=pairs,independent_blocks=len(blocks),candidate_over_parent=point,pointwise_two_sided_95=[lo,hi],latency_reduction=1-point,latency_reduction_95=[1-hi,1-lo],marginal_median_ns={s:median(v) for s,v in values.items()},median_paired_saving_ns=median(saving),block_log_ratios=blocks)
if (H/'safety-full-1/results.json').exists():
 safety=load('safety-full-1/results.json')
 result['safety']=dict(processes=len(safety),passed=sum(r['totals'][0] for r in safety),failed=sum(r['totals'][1] for r in safety),skipped=sum(r['totals'][2] for r in safety),complete=len(safety)==12 and all(r['passed'] for r in safety),limits=['PaintDevice stressTestMemoryFragmentation excluded after candidate and frozen parent SIGSEGV; all other methods run, no full-group qualification'])
if (H/'mechanism-results.json').exists():
 rows=load('mechanism-results.json');assert len(rows)==4 and all(r['passed'] for r in rows)
 observed=[]
 for r in rows:
  stages={s['stage']:s for s in r['snapshots']};roles={}
  for role in ['node.paint','root.original']:
   before=next(d for d in stages['Setup']['devices'] if d['role']==role);after=next(d for d in stages['Stroke']['devices'] if d['role']==role)
   roles[role]={k:after[k]-before[k] for k in before if k not in ['backend','role']}
  node=roles['node.paint'];root=roles['root.original']
  assert node['mutation.writablePinsAcquired']==node['mutation.writablePinsReleased']==(2420 if r['side']=='parent' else 152)
  for key,value in {'mutation.generationsReserved':76,'mutation.operationSessionsCreated':27,'mutation.sessionsCreated':27,'mutation.pagesSealed':76,'work.nativeDuplicatePages':20,'work.defaultInitializedPages':56,'publication.installedMutationCommits':1}.items():assert node[key]==value,(r['index'],key,node[key])
  for key,value in {'mutation.generationsReserved':132,'work.nativeDuplicatePages':72,'work.defaultInitializedPages':60,'mutation.writablePinsAcquired':228}.items():assert root[key]==value,(r['index'],key,root[key])
  assert r['sample']['projection_updates']==19
  observed.append(dict(index=r['index'],side=r['side'],roles=roles))
 result['mechanism']=dict(observations=observed,predicted_node_pins=[2420,152],deleted_pairs=2268,pin_reduction=2268/2420,fixed_node_other_work_prediction_met=True,timing_excluded=True,root_commit_note='Initial analyzer incorrectly treated pretrace root commits11 as invariant. Same frozen parent produces12/13; candidate12/12. Preserve observations, no resampling; no root commit deletion claimed. Node commit1, root generations/copy/init/pins and projection updates remain invariant.')
if (H/'visit-results.json').exists():
 rows=load('visit-results.json');assert len(rows)==4 and all(r['passed'] for r in rows)
 observations=[]
 for r in rows:
  fixed=[v for v in r['visits'] if v['fixed']];assert len(fixed)==27 and all(v['succeeded'] and not v['selection'] for v in fixed)
  totals={k:sum(v[k] for v in fixed) for k in ['P','R','F','C']};assert totals==dict(P=76,R=2344 if r['side']=='parent' else 76,F=5363,C=76),totals
  observations.append(dict(index=r['index'],side=r['side'],totals=totals,maximum_F=max(v['F'] for v in fixed),maximum_P=max(v['P'] for v in fixed)))
 result['visits']=dict(observations=observations,E=0,semantic_work_unchanged=True,maximum_fragment_payload_capacity_bytes=516*24+4*8,largest_four_operation_payload_capacity_sum_bytes=45728,capacity_note='sizeof rect24 / size_t8 for both64bit targets; payload capacity bound only, not measured concurrent physical residency/allocator overhead')
if (H/'hold-results.json').exists():
 rows=load('hold-results.json');assert len(rows)==2 and all(r['passed'] for r in rows)
 result['holds']=[dict(persistent=r['persistent'],fixed_pins=sum(h['pins'] for h,v in zip(r['holds'],r['visits']) if v['fixed']),maximum_fixed_hold_ns=max(h['maximum_ns'] for h,v in zip(r['holds'],r['visits']) if v['fixed']),total_fixed_hold_ns=sum(h['total_ns'] for h,v in zip(r['holds'],r['visits']) if v['fixed'])) for r in rows]
if (H/'performance-results.json').exists():
 rows=load('performance-results.json');assert len(rows)==100 and all(r['passed'] for r in rows)
 result['performance']={arch:{endpoint:estimate([r for r in rows if r['phase']=='paired' and r['arch']==arch],24,endpoint,261019) for endpoint in ['stroke_to_projection_ready_ns','pen_up_to_projection_ready_ns','undo_drain_ns','redo_drain_ns','owner_teardown_ns']} for arch in ['arm64','x86_64']}
if (H/'lowreuse-1-results.json').exists():
 rows=load('lowreuse-1-results.json');assert len(rows)==96 and all(r['passed'] for r in rows)
 result['lowreuse']={arch:{str(pattern):estimate([r for r in rows if r['arch']==arch and r['pattern']==pattern],12,'loop_ns',261020) for pattern in [0,1]} for arch in ['arm64','x86_64']}
for family in ['fresh','history']:
 path=H/('controls-'+family+'-summary.json')
 if path.exists():result['controls_'+family]=load(path.name)
result['qualification']=dict(blueprint_mechanism_verified='visits' in result and 'mechanism' in result,M6_complete=False,remaining=['formal calibration2/20 unchanged','metadata residency pre-reconstruction equivalent denominator missing','CP0 full required qualification missing','original memory fragmentation overlapping-page stress remains unsafe; not fixed by this batch'])
result['decision']='Candidate implemented and tested, business speedup unconfirmed; retain experiment branch and evidence, revert complete candidate on working branch. No partial const/sort patch retained.'
if (H/'safety-full-rollback/results.json').exists():
 rows=load('safety-full-rollback/results.json');result['rollback_safety']=dict(processes=len(rows),passed=sum(r['totals'][0] for r in rows),failed=sum(r['totals'][1] for r in rows),skipped=sum(r['totals'][2] for r in rows),complete=len(rows)==12 and all(r['passed'] for r in rows),same_stress_exclusion=True)
(H/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k in ['safety','holds','qualification']},indent=2))
for name in ['performance','lowreuse']:
 for arch,group in result.get(name,{}).items():
  for key,v in group.items():print(name,arch,key,'reduction',v['latency_reduction'],'95%',v['latency_reduction_95'])
