import json, statistics as st, random, hashlib, sys, math
from pathlib import Path
p=Path(__file__).resolve().parent;phase=['setup','write','read','finish','undo','redo','teardown']
put=lambda n,v:(p/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def metrics(run):
 r=run['coverage'][0];v={}
 if run.get('mode')==2:
  empty=r['empty_main_instructions_raw']/r['empty_replays']
  for i,n in enumerate(phase):v[n+'_instructions']=r['phase_main_instructions_raw'][i]-empty*r['phase_calls'][i]
  v['phase_sum_instructions']=sum(v.values())
  v['main_instructions']=r['main_instructions'];v['process_instructions']=r['kernel']['ri_instructions']
  v['main_outside_phases_instructions']=v['main_instructions']-v['phase_sum_instructions']
  v['process_minus_main_instructions']=v['process_instructions']-v['main_instructions']
  v['write_instructions_per_page']=v['write_instructions']/(r['pages']*r['writes']*r['lifetimes'])
 else:
  for n in phase:
   for t in ['cpu','thread_cpu','wall']:v[n+'_'+t+'_ms']=r[n][t+'_ns']/1e6
  for n in ['process','foreground','wall']:v[n+'_ms']=r[n+'_ns']/1e6
  v['tail_cpu_ms']=r['tail_cpu_ns']/1e6
  v['whole_child_cpu_ms']=1000*(run['whole_child']['user_cpu_s']+run['whole_child']['system_cpu_s'])
 return v
stage=sys.argv[1]
if stage=='forecast':
 runs=json.loads((p/'calibration/RUNS.json').read_text());assert len(runs)==12 and all(x['passed'] for x in runs)
 out={'basis':'Independent complete-construction calibration, after implementation; not a pre-implementation forecast, strict algorithm upper, or confidence guarantee','cases':{}}
 for case in [3,7]:
  values={tag:[metrics(x) for x in runs if x['case']==case and x['tag']==tag] for tag in ['P','U','N']}
  prices={tag:{k:st.mean(v[k] for v in rows) for k in rows[0]} for tag,rows in values.items()}
  out['cases'][str(case)]={'prices':prices,'integration_added_write':prices['N']['write_instructions']-prices['U']['write_instructions'],'retained_net_write':prices['P']['write_instructions']-prices['N']['write_instructions'],'engineering_planning_band_N_write':[.95*prices['N']['write_instructions'],1.05*prices['N']['write_instructions']]}
 put('FORECAST.json',out);q=json.loads((p/'VALIDATION_PROTOCOL.json').read_text());q['forecast_sha256']=hashlib.sha256((p/'FORECAST.json').read_bytes()).hexdigest();put('VALIDATION_PROTOCOL.json',q)
 print(json.dumps({k:{'N_write':v['prices']['N']['write_instructions'],'added':v['integration_added_write'],'retained':v['retained_net_write']} for k,v in out['cases'].items()},indent=2))
elif stage=='fresh':
 runs=json.loads((p/'fresh/RUNS.json').read_text());assert len(runs)==160 and all(x['passed'] for x in runs)
 rng=random.Random(260926);out=[]
 for bucket in ['write-n64-k1-b4','write-n1024-k16-b4']:
  blocks=[];pairdata=[]
  for b in range(20):
   ratios=[]
   for pair in [0,1]:
    values={x['tag']:x['coverage'][0]['completed_operations']*1e9/x['coverage'][0]['wall_ns'] for x in runs if x['bucket']==bucket and x['block']==b and x['pair']==pair}
    ratio=values['N']/values['P'];ratios.append(ratio);pairdata.append(dict(block=b,pair=pair,throughput=values,ratio=ratio))
   blocks.append(math.sqrt(ratios[0]*ratios[1]))
  boots=sorted(st.median(rng.choices(blocks,k=20)) for _ in range(50000));lower=boots[1250]
  out.append(dict(bucket=bucket,median_ratio=st.median(blocks),lower97_5=lower,required=.98,passed=lower>=.98,blocks=blocks,pairs=pairdata))
 put('FRESH_RESULT.json',{'buckets':out,'passed':all(x['passed'] for x in out),'scope':json.loads((p/'FRESH_PROTOCOL.json').read_text())['scope']});print([(x['bucket'],x['median_ratio'],x['lower97_5'],x['passed']) for x in out])
else:
 runs=json.loads((p/'validation/RUNS.json').read_text());assert len(runs)==144 and all(x['passed'] for x in runs)
 forecast=json.loads((p/'FORECAST.json').read_text());out={};rng=random.Random(261103)
 # Fixed paired triad blocks, mean differences and pointwise 95% intervals.
 indices=[[rng.randrange(12) for _ in range(12)] for _ in range(50000)]
 def estimate(v):
  boot=sorted(sum(v[i] for i in idx)/12 for idx in indices)
  return {'mean':st.mean(v),'ci95':[boot[1250],boot[48750]],'samples':v}
 for case in [3,7]:
  c={}
  for mode in [0,2]:
   values={tag:[metrics(next(x for x in runs if x['case']==case and x['mode']==mode and x['tag']==tag and x['block']==b)) for b in range(12)] for tag in ['P','U','N']}
   c[str(mode)]={'prices':{t:{k:st.mean(r[k] for r in rows) for k in rows[0]} for t,rows in values.items()},'differences':{}}
   for name,a,b in [('integration_added','N','U'),('retained_net','P','N'),('prior_net','P','U')]:
    c[str(mode)]['differences'][name]={k:estimate([values[a][i][k]-values[b][i][k] for i in range(12)]) for k in values[a][0]}
  prices=c['2']['prices'];r,u,v=[prices[t]['write_instructions'] for t in ['P','U','N']]
  c['warm_write_summary']={'P':r,'U':u,'N':v,'per_page':v/1024,'added_contract':v-u,'retained_net':r-v,'net_percent':100*(r-v)/r,'prior_saving_retained_percent':100*(r-v)/(r-u),'forecast_error_percent':100*(v/forecast['cases'][str(case)]['prices']['N']['write_instructions']-1)}
  out[str(case)]=c
 put('JOINT_RESULT.json',out);print(json.dumps({k:v['warm_write_summary'] for k,v in out.items()},indent=2))
