import json, os, re, time, subprocess, hashlib, sys
from pathlib import Path
p=Path(__file__).resolve().parent;integration=p.parent;base=Path('/Users/apple/krita_gpu/krita/_build-br0-cpu')
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
stage=sys.argv[1];protocol=json.loads((p/(stage.upper()+'_PROTOCOL.json')).read_text())
gate=json.loads((p/'JOINT_GATE.json').read_text());assert gate['semantic_structure_complete']
for f,h in gate['artifacts'].items():assert sha(f)==h,f
if stage=='validation':assert protocol['forecast_sha256']==sha(p/'FORECAST.json')
identities=json.loads((p/'IDENTITIES.json').read_text())
for tag,v in identities.items():
 assert sha(v['library'])==v['library_sha256']
 assert sha(v['binary'])==v['binary_sha256']
jobs=protocol['jobs']
if stage=='validation':
 for case in [3,7]:
  for mode in [0,2]:
   orders=[tuple(j['tag'] for j in jobs if j['block']==b and j['case']==case and j['mode']==mode) for b in range(12)]
   for a,b in [('P','N'),('U','N'),('P','U')]:assert sum(o.index(a)<o.index(b) for o in orders)==6
if stage=='fresh':
 for bucket in ['write-n64-k1-b4','write-n1024-k16-b4']:
  orders=[tuple(j['tag'] for j in jobs if j['bucket']==bucket and j['block']==b and j['pair']==i) for b in range(20) for i in range(2)]
  assert orders.count(('P','N'))==20 and orders.count(('N','P'))==20
folder=p/stage;folder.mkdir(exist_ok=False)
identities=json.loads((p/'IDENTITIES.json').read_text());runtimes={t:Path(v['library']).parent for t,v in identities.items()}
env={k:v for k,v in os.environ.items() if not k.startswith(('DYLD_','BR1_','KIS_BR1_','KRITA_NATIVE_'))}
env.update(QT_QPA_PLATFORM='offscreen',QT_HASH_SEED='0',KIS_TEST_PREFIX_PATH='/Users/apple/krita_gpu/krita/_install',QT_PLUGIN_PATH='/Users/apple/krita_gpu/krita/_install/plugins',KIS_TEST_PLUGIN_PATH=str(base/'bin'),BR1_ACCOUNT56='0')
records=[]
for index,j in enumerate(jobs):
 tag=j['tag'];library=runtimes[tag]/'libkritaimage.21.0.0.dylib'
 binary=Path(identities[tag]['binary'])
 settings=['DYLD_LIBRARY_PATH='+str(library.parent)+(':'+str(integration/'build/bin') if tag=='N' else '')+':'+str(base/'bin'),'DYLD_PRINT_LIBRARIES=1']
 if tag=='U':settings+=['KRITA_NATIVE_RESULT_PROTOCOL=104']
 if stage=='fresh':
  binary=p/'fresh-P' if tag=='P' else integration/'build/bin/kis_tiles3_cpu_baseline_test'
  settings+=['KIS_CPU_BASELINE_LOOPS=4','KIS_CPU_BASELINE_RATE_MS=750','KIS_BR1_STAGE_PROFILE=0']
  if tag=='N':settings+=['KRITA_NATIVE_RESULT_FORCE_FRESH=1']
  arguments=['testSharedBaseline:'+j['bucket']]
 else:
  settings+=['BR1_MODE52='+str(j['mode']),'BR1_SLOW_COUNTERS='+str(int(j['mode']>0)),'BR1_LIFETIMES=4','BR1_CASE='+str(j['case']),'BR1_SIDE104=256','BR1_WRITES104=16']
  arguments=[]
 cmd=['arch','-arm64','/usr/bin/env',*settings,str(binary),*arguments];log=folder/('run-%03d.log'%index);start=time.monotonic()
 with log.open('x') as f:
  proc=subprocess.Popen(cmd,cwd=base,env=env,stdout=f,stderr=subprocess.STDOUT)
  while True:
   pid,status,usage=os.wait4(proc.pid,os.WNOHANG)
   if pid:proc.returncode=os.waitstatus_to_exitcode(status);break
   if time.monotonic()-start>120:
    proc.kill();pid,status,usage=os.wait4(proc.pid,0);proc.returncode=os.waitstatus_to_exitcode(status);break
   time.sleep(.02)
 s=log.read_text();pattern=r'CPU_BASELINE (\{.+\})' if stage=='fresh' else r'^BR1_COVERAGE (.+)$'
 rows=[json.loads(x) for x in re.findall(pattern,s,re.M)]
 loaded=[l for l in s.splitlines() if l.startswith('dyld[') and str(library.resolve()) in l]
 ok=proc.returncode==0 and len(rows)==1 and bool(loaded)
 if ok:
  row=rows[0]
  if stage=='fresh':ok &= row['correctness']=='Pass' and row['wall_ns']>=750000000 and row['rate_check_interval']==64
  else:
   ok &= row['semantic_ok'] and row['accepted']
   if j['mode']==2:ok &= row['phase_calls']==[4,64,64,4,4 if j['case']==7 else 0,4 if j['case']==7 else 0,4]
 records.append(dict(**j,command=cmd,exit=proc.returncode,pid=proc.pid,reaped=True,elapsed_s=time.monotonic()-start,loaded=loaded,binary_sha256=sha(binary),library_sha256=sha(library),log=str(log),log_sha256=sha(log),coverage=rows,whole_child=dict(user_cpu_s=usage.ru_utime,system_cpu_s=usage.ru_stime,max_rss_native=usage.ru_maxrss),passed=bool(ok)))
 (folder/'RUNS.json').write_text(json.dumps(records,indent=2));print(stage,index,j,'PASS' if ok else 'FAIL',flush=True)
 if not ok:raise SystemExit('failed original retained; stop, no replacements')
