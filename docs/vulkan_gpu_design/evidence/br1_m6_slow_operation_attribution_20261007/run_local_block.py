from pathlib import Path
import hashlib,json,os,re,resource,statistics,subprocess,time
H=Path(__file__).resolve().parent;R=H.parents[3]/'krita';B=R/'_build-br0-cpu'
P=H.parent/'br1_m6_provider_borrow_20261006';D=H.parent/'br1_m6_calibration_resolution_20261006'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
freeze=json.loads((H/'local-block-freeze.json').read_text())
for p,w in freeze['files'].items():assert sha(p)==w,p
O=H/'local-block';O.mkdir();runs=[];resource.setrlimit(resource.RLIMIT_CORE,(0,0))
baseenv=dict(os.environ,QT_QPA_PLATFORM='offscreen',KIS_BR1_PROFILE='0',KIS_BR1_STAGE_PROFILE='0',
 KIS_TEST_PREFIX_PATH=str(R/'_install'),KIS_TEST_PLUGIN_PATH=str(B/'bin'),M6_DIAGNOSTIC_QOS='unchanged')
baseenv.pop('QT_HASH_SEED',None);baseenv.pop('M6_MECHANISM',None)
groups=[('arm64',1,'native-pin','same'),('arm64',16,'hit','cross'),
 ('x86_64',1,'native-pin','same'),('x86_64',1,'native-pin','cross')]
def run(block,policy,group,pair,arm):
 arch,k,case,cell=group;libdir=P/'selection-image' if arm and cell=='cross' else B/'bin'
 cmd=['arch','-'+arch,'/usr/bin/env','DYLD_LIBRARY_PATH='+str(libdir)+':'+str(B/'bin'),
  'DYLD_PRINT_LIBRARIES=1',str(D/f'probe-seed-{arch}/probe'),'fixed',case,str(k),'0','512000000','8',str(pair%2),'128']
 log=O/f'{len(runs):03d}-{policy}-{arch}-k{k}-{case}-{cell}-b{block}-p{pair}-a{arm}.log'
 start=time.monotonic()
 with log.open('x') as f:
  child=subprocess.Popen(cmd,cwd=R,env=baseenv,stdout=f,stderr=subprocess.STDOUT)
  try:code=child.wait(timeout=120);timeout=False
  except subprocess.TimeoutExpired:child.kill();code=child.wait(timeout=5);timeout=True
 raw=log.read_text();row=dict(block=block,policy=policy,arch=arch,K=k,case=case,cell=cell,pair=pair,arm=arm,
  command=cmd,start_monotonic=start,seconds=time.monotonic()-start,pid=child.pid,exit_code=code,timed_out=timeout,
  reaped=True,log=log.name,loaded_image=str(libdir/'libkritaimage.21.0.0.dylib') in raw,
  failures=re.findall(r'^.*(?:FAIL!|FATAL|SAFE ASSERT|ASSERT failure|sample_failed).*$',raw,re.M))
 runs.append(row);log.with_suffix('.json').write_text(json.dumps(row,indent=2)+'\n')
 assert code==0 and not timeout and row['loaded_image'] and not row['failures'] and 'all_checks_passed=1' in raw,row
 data=json.loads(next(t[7:] for t in raw.splitlines() if t.startswith('WINDOW ')))
 assert not data['paired'] and data['switch_loaded']==(cell=='cross' and arm==1)
 a=data['arms'][0];ns=a.pop('operation_ns');n=len(ns)
 assert n==a['completed'] and sum(ns)==a['wall_ns'] and min(ns)>0 and sum(ns)>=512000000 and n>=128
 assert a['handoffs']==(n*k if case=='hit' else 0) and a['copy_bytes']==(0 if case=='hit' else n*k*16384)
 a.update(throughput=n*1e9/sum(ns),median_ns=statistics.median(ns),maximum_ns=max(ns),
  vector_sha256=hashlib.sha256(json.dumps(ns).encode()).hexdigest())
 row.update(observation=a,qos=json.loads(next(t[4:] for t in raw.splitlines() if t.startswith('ENV '))),
  layout=json.loads(next(t[7:] for t in raw.splitlines() if t.startswith('LAYOUT '))))
 assert row['qos']['qos_before']==row['qos']['qos_after']==33 and row['layout']['hash_seed']!=0
 log.with_suffix('.json').write_text(json.dumps(row,indent=2)+'\n')
for block in range(6):
 offset=block%4;gs=groups[offset:]+groups[:offset]
 for policy in (['global','local'] if block%2==0 else ['local','global']):
  if policy=='global':
   for pair in range(2):
    for g in (gs if pair==0 else list(reversed(gs))):
     for arm in ([0,1] if (block+pair)%2==0 else [1,0]):run(block,policy,g,pair,arm)
  else:
   for g in gs:
    for pair in range(2):
     for arm in ([0,1] if (block+pair)%2==0 else [1,0]):run(block,policy,g,pair,arm)
 print(json.dumps({'block':block+1,'processes':len(runs)}),flush=True)
assert len(runs)==192
for p,w in freeze['files'].items():assert sha(p)==w,p
(O/'runs.json').write_text(json.dumps(runs,indent=2)+'\n')
(O/'identity-final.json').write_text(json.dumps({'verified':True,'files':freeze['files']},indent=2)+'\n')
print('complete192; semantic/exit/image/identity passed',flush=True)
