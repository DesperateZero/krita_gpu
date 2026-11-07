"""Work/count closure, predeclared scaling and out-of-sample residuals."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import statistics

HERE=Path(__file__).resolve().parent
rows=json.loads((HERE/'results.json').read_text())
protocol=json.loads((HERE/'protocol.json').read_text())
assert len(rows)==protocol['total_processes']==98
before=json.loads((HERE/'identity-before.json').read_text())
after=json.loads((HERE/'identity-final.json').read_text())
assert after['inputs_verified'] and after['hashes']==before
FIELDS=['fits_locked','control_allocate','storage_owner_allocate','storage_owner_deallocate',
        'storage_owner_deref','local_prepare','parent_prepare','local_settle','parent_settle',
        'raw_control_free','local_release_live','parent_release_live']
cells=defaultdict(list)
count_cells=[]
work_checks=[]
for row in rows:
 assert row['exit_code']==0 and not row['timed_out'] and row['reaped'] and row['image_loaded'] and row['checks_passed']
 assert len(row['data'])==1
 d=row['data'][0];n,k,b,h=row['row'];operations=d['completed']
 assert d['management_counter_active']==row['count']
 c=d['steady_counts'];full=h==64
 prediction={'duplicate_pages':0 if full else k,'duplicate_bytes':0 if full else k*4096*b,
             'foreground_copy_bytes':0 if full else k*4096*b,'preclone_hits':0,
             'payload_pages':k if full else 0,'payload_bytes':k*4096*b if full else 0,
             'default_bytes':0,'generations':k,'sessions':1,'sealed_pages':k,'commits':1}
 assert all(c[name]==value*operations for name,value in prediction.items()),(row['row'],c,prediction)
 assert all(d['first_counts'][name]==value for name,value in prediction.items())
 assert d['logical_bytes_per_op']==k*64*b*h
 metrics={name:value/operations for name,value in d['steady_metadata'].items()}
 assert metrics['local_sequences_non_reclamation']==2*k
 assert metrics['local_version_inputs_non_reclamation']==3*k
 assert metrics['mutation_base_inputs_non_reclamation']==k
 assert metrics['full_snapshot_exports_non_reclamation']==metrics['full_snapshot_version_inputs_non_reclamation']==0
 assert metrics['publication_lookup_inputs']==metrics['prepared_mutation_pages']==0
 first_metrics=d['first_metadata']
 assert first_metrics['local_sequences_non_reclamation']==2*k
 assert first_metrics['local_version_inputs_non_reclamation']==3*k
 assert first_metrics['mutation_base_inputs_non_reclamation']==k
 assert first_metrics['full_snapshot_exports_non_reclamation']==first_metrics['full_snapshot_version_inputs_non_reclamation']==0
 assert first_metrics['publication_lookup_inputs']==first_metrics['prepared_mutation_pages']==0
 work_checks.append({'variant':row['variant'],'block':row['block'],'count':row['count'],
                     'row':row['row'],'completed':operations,'predicted_per_op':prediction,
                     'metadata_per_op':metrics,'first_metadata':first_metrics,'prediction_errors':0})
 if row['count']:
  counts=dict(zip(FIELDS,(v/operations for v in d['steady_management'])))
  assert counts['local_prepare']==counts['parent_prepare']==counts['local_settle']==counts['parent_settle']
  count_cells.append({'row':row['row'],'counts':counts,'first_counts':dict(zip(FIELDS,d['first_management'])),
                      'metadata':metrics,'completed':operations})
 else:
  assert not any(d['steady_management'])
  cells[(row['variant'],n,k,b,h)].append({'wall_us':d['wall_ns']/operations/1000,
            'thread_us':d['thread_cpu_ns']/operations/1000,'process_us':d['process_cpu_ns']/operations/1000,
            'metadata':metrics,'block':row['block']})
timing=[]
for key,values in sorted(cells.items()):
 assert len(values)==3
 timing.append({'variant':key[0],'row':list(key[1:]),'samples':values,
   **{metric:{'median':statistics.median(v[metric] for v in values),
              'min':min(v[metric] for v in values),'max':max(v[metric] for v in values)}
      for metric in ('wall_us','thread_us','process_us')}})

def fit(points):
 x=[p[0] for p in points];y=[p[1] for p in points]
 mx,my=statistics.mean(x),statistics.mean(y)
 slope=sum((a-mx)*(b-my) for a,b in points)/sum((a-mx)**2 for a in x)
 intercept=my-slope*mx
 residuals=[{'K':a,'actual':b,'predicted':intercept+slope*a,'error':b-intercept-slope*a,
             'relative_error_percent':100*(b-intercept-slope*a)/b if b else None} for a,b in points]
 sse=sum(r['error']**2 for r in residuals);sst=sum((b-my)**2 for b in y)
 return {'intercept':intercept,'per_page_slope':slope,'r_squared':1-sse/sst if sst else None,
         'all_residuals':residuals,'maximum_absolute_error':max(abs(r['error']) for r in residuals)}

timing_models=[]
for variant in ('m5','current'):
 for n in (64,1024):
  selected=[r for r in timing if r['variant']==variant and r['row'][0]==n and r['row'][2:]==[4,1]]
  for metric in ('wall_us','thread_us','process_us'):
   timing_models.append({'variant':variant,'N':n,'metric':metric,
                         **fit([(r['row'][1],r[metric]['median']) for r in selected])})
count_models=[]
for n in (64,1024):
 selected=[r for r in count_cells if r['row'][0]==n and r['row'][2:]==[4,1]]
 for field in FIELDS:
  train=[r for r in selected if r['row'][1] in (1,2,4,16)]
  model=fit([(r['row'][1],r['counts'][field]) for r in train])
  holdout=[]
  for r in selected:
   if r['row'][1] not in (8,32):continue
   actual=r['counts'][field];pred=model['intercept']+model['per_page_slope']*r['row'][1]
   holdout.append({'K':r['row'][1],'actual':actual,'predicted':pred,'error':actual-pred,
                   'relative_error_percent':100*(actual-pred)/actual if actual else None})
  count_models.append({'N':n,'field':field,'training_K':[1,2,4,16],**model,'holdouts':holdout})

# Post-measurement source-derived model refinement, using the already frozen
# grid. Balanced initialization and replacements preserve AVL shape/height.
# Current sparse commit copies each union-path node once; dense rebuild copies
# every N-node root. M5 sparse commit path-copies separately for each page.
def tree(lo,hi):
 if lo>=hi:return None
 mid=(lo+hi)//2
 return (mid,tree(lo,mid),tree(mid+1,hi))
def path(root,key):
 result=[]
 while root:
  result.append(root[0])
  if key==root[0]:return result
  root=root[1] if key<root[0] else root[2]
 raise AssertionError(key)
root_work=[]
for n in (64,1024):
 root=tree(0,n)
 for k in (1,2,4,8,16,32):
  paths=[path(root,key) for key in range(k)]
  union=len(set().union(*map(set,paths)));dense=k>=(n+3)//4
  current_nodes=n if dense else union
  m5_nodes=n if dense else sum(map(len,paths))
  root_work.append({'N':n,'K':k,'dense':dense,'sparse_union_nodes':union,
   'current_nodes_constructed_source_prediction':current_nodes,
   'm5_nodes_constructed_source_prediction':m5_nodes,
   'current_root_control_requests_source_prediction':2*current_nodes+int(dense),
   'current_root_fits_source_prediction':4*current_nodes+2*int(dense),
   'metadata_unique_check_pairs_source_prediction':k*(k-1)//2})
root_validation=[]
for k in (1,2,4,8,16,32):
 observed={n:next(r for r in count_cells if r['row']==[n,k,4,1]) for n in (64,1024)}
 predicted={n:next(r for r in root_work if r['N']==n and r['K']==k) for n in (64,1024)}
 for field,root_field in [('control_allocate','current_root_control_requests_source_prediction'),
                           ('fits_locked','current_root_fits_source_prediction')]:
  reference_base=observed[1024]['first_counts'][field]-predicted[1024][root_field]
  prediction=reference_base+predicted[64][root_field]
  actual=observed[64]['first_counts'][field]
  root_validation.append({'K':k,'field':field,'reference_N':1024,'holdout_N':64,
    'non_root_reference_count':reference_base,'predicted_first':prediction,'actual_first':actual,
    'error':actual-prediction,
    'steady_cross_N_error_after_same_root_adjustment':
      observed[64]['counts'][field]-observed[1024]['counts'][field]
      -predicted[64][root_field]+predicted[1024][root_field]})
closure={
 'qualification':'Diagnostic whole-path workload/scaling; no causal coefficients or formal gate pass',
 'counts_scope':'Calling-thread budget counters; metadata subtracts explicit reclamation subset, other readers may remain',
 'timing':timing,'work_checks':work_checks,'count_cells':count_cells,
 'timing_affine_models_descriptive':timing_models,'count_affine_models_with_holdouts':count_models,
 'source_derived_root_work':root_work,
 'post_measurement_root_model_cross_N_validation':root_validation,
 'known_unclosed':'Per-allocation lifetime/retry/state dependence, CPU sample mix vs whole loop, scheduling/lock wall and final background drain; no ideal microsecond claim',
}
(HERE/'algorithm-budget.json').write_text(json.dumps(closure,indent=2)+'\n')
print('98 processes: pixel/local logical work predictions exact; publication retries retained')
for r in timing_models:
 if r['metric']=='thread_us':print(r['variant'],r['N'],'CPU fit',round(r['intercept'],2),round(r['per_page_slope'],2),'R2',round(r['r_squared'],4),'max residual',round(r['maximum_absolute_error'],2))
for n in (64,1024):
 print('N',n,'count holdout errors',[(r['field'],[(h['K'],round(h['relative_error_percent'],2)) for h in r['holdouts']])
    for r in count_models if r['N']==n and r['field'] in ('control_allocate','fits_locked','storage_owner_deref')])
print('Source-derived root model first-operation cross-N residuals', [r['error'] for r in root_validation])
for r in root_work:
 if r['K']==16:print('K16 root work',r)
