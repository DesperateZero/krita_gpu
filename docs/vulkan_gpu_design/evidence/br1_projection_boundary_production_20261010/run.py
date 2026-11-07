#!/usr/bin/env python3
import argparse,hashlib,json,os,re,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];B=R/'krita/_build-br0-cpu';OLD=H.parent/'br1_projection_boundary_trial_20261010'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('batch',choices=['tests','capability','confirm','tests-r1','capability-r1','confirm-r1','tests-x86-r1']);args=a.parse_args();kind=args.batch.split('-')[0];suffix='-r1' if args.batch.endswith('-r1') else ''
fixture=H.parent/'br1_upstream_cost_accounting_20261007/fixture-current/probe'
libs={'parent':H/'parent-lib/libkritaimage.21.0.0.dylib','candidate':B/'bin/libkritaimage.21.0.0.dylib','parent-count':OLD/'prototype-r1/libkritaimage.21.0.0.dylib','candidate-count':H/('observed'+suffix)/'libkritaimage.21.0.0.dylib'}
assert sha(libs['parent'])=='ba5876d6b155e84f27087577d50243c6913cb4a62236634699b3a2d57b12e612'
manager_tests=['testPageStoreClearCompositePressure','testPageStorePartialDefaultClearStaysSparse','testPageStorePixelOperation','testPageStorePixelOperationCanonicalRange','testPageStorePixelOperationPreflightBudgetPressure','testPageStoreChangedStorageBudget','testPageStorePixelOperationBorrowed','testPageStorePixelOperationConcurrent','testPageStoreAdapterPreparationRefusal','testPageStoreAdapterAfterAbort','testPageStoreAdapterBarrier','testPageStoreAdapterDelivery','testPageStoreAdapterDeliveryLifetime','testPageStoreAdapterDeliveryLegacyConflict','testPageStoreCancelledPrivateClient','testPageStoreDefaultLifecycleDoesNotMaterialize','testPageStoreAbortUnderBudgetPressure','testPageStoreClearBarrierCancelsLegacyWriter']
if kind=='tests':sequence=[('candidate',B/'bin'/t,manager_tests if t=='kis_tiled_data_manager_test' else []) for t in ['kis_painter_test','kis_async_merger_test','kis_projection_test','kis_tiled_data_manager_test']]
elif kind=='capability':sequence=[(c,fixture,['testMatchedCpuBaseline']) for c in ['parent-count','candidate-count','candidate-count','parent-count']]
else:
 for required in ['tests','capability']:assert all(x['passed'] for x in json.loads((H/(required+suffix)/'results.json').read_text()))
 sequence=[(c,fixture,['testMatchedCpuBaseline']) for c in ['parent','candidate','candidate','parent','candidate','parent','parent','candidate']*8]
identity={str(p):sha(p) for p in [Path(__file__),H/'PROTOCOL.md',H/'PRE_CONFIRMATION.md',H/'analyze.py',H/'R1_PROTOCOL.md',fixture]+list({libs[c] for c,_,_ in sequence})+list({e for _,e,_ in sequence})}
source=subprocess.check_output(['git','diff','--binary'],cwd=R/'krita');outroot=H/args.batch;outroot.mkdir();(outroot/'source.diff').write_bytes(source)
(outroot/'identity-before.json').write_text(json.dumps(identity,indent=2)+'\n');(outroot/'protocol.md').write_bytes((H/'PROTOCOL.md').read_bytes())
records=[]
for index,(config,executable,selectors) in enumerate(sequence):
 out=outroot/f'{index:02}-{config}';out.mkdir();lib=libs[config]
 command=['arch','-x86_64' if 'x86' in args.batch else '-arm64','/usr/bin/env','DYLD_LIBRARY_PATH='+str(lib.parent)+':'+str(B/'bin'),'DYLD_PRINT_LIBRARIES=1',str(executable)]+selectors+['-nocrashhandler']
 env={k:v for k,v in os.environ.items() if not k.startswith(('DYLD_','BR1_')) and k not in ['QT_HASH_SEED','M6_MECHANISM']}
 overrides=dict(QT_QPA_PLATFORM='offscreen',KIS_BR1_SEED='12345',KIS_BR1_PROFILE='0',KIS_BR1_STAGE_PROFILE='0',KIS_TEST_PREFIX_PATH=str(R/'krita/_install'),KIS_TEST_PLUGIN_PATH=str(OLD/'test-plugins' if kind=='tests' else R/'build/br1-cp0-20261003/current-plugins'))
 if config=='parent-count':overrides.update(BR1_BOUNDARY_FUSE='0',BR1_BOUNDARY_COUNT='1')
 env.update(overrides);start=time.monotonic()
 with (out/'fixture.log').open('x') as log:
  proc=subprocess.Popen(command,cwd=R/'krita',env=env,stdout=log,stderr=subprocess.STDOUT)
  (out/'command.json').write_text(json.dumps(dict(command=command,env=overrides,cwd=str(R/'krita'),pid=proc.pid),indent=2)+'\n')
  try:code,timeout=proc.wait(timeout=180 if kind=='tests' else 120),False
  except subprocess.TimeoutExpired:proc.kill();code,timeout=proc.wait(timeout=5),True
 txt=(out/'fixture.log').read_text();parse=lambda prefix:[json.loads(s) for s in re.findall(prefix+r' (\{[^\n]+\})',txt)]
 samples,stages,counts=[parse(x) for x in ['BR1_CP0_JSON','BR1_COST_STAGE','BR1_BOUNDARY_COUNT']];totals=re.findall(r'Totals: (\d+) passed, (\d+) failed, (\d+) skipped',txt)
 loaded={str(Path(x).resolve()) for x in re.findall(r'^dyld\[\d+\]: <[^>]+> (.+)$',txt,re.M) if Path(x).is_file() and str(Path(x).resolve()).startswith(str(R))}
 runtime={x:sha(x) for x in sorted(loaded)};(out/'runtime.json').write_text(json.dumps(runtime,indent=2)+'\n');loading=str(lib.resolve()) in loaded
 if executable==fixture:
  semantic=len(samples)==1 and samples[0]['painted_sha256']=='2c9ae317c3fe2f5f9931c0c354aea3734e69433e67aabdba85d42633ea76df29' and samples[0]['blank_sha256']=='30e14955ebf1352266dc2ff8067e68104607e750abb9d3b36582b8af909fcb58' and samples[0]['segment_callbacks']==8 and samples[0]['update_callbacks']==4 and samples[0]['projection_updates']>0 and samples[0]['image_destroyed'] and samples[0]['strategy_destroyed']
  observation=len(stages)==5 and [s['stage'] for s in stages]==['Setup','Stroke','Undo','Redo','Teardown'] and all(s['cpu_ns']>0 and abs(s['cpu_ns']-s['user_ns']-s['system_ns'])<100000 for s in stages) and (len(counts)==6 if config.endswith('-count') else not counts)
  expected=totals==[('3','0','0')]
 else:semantic=bool(totals) and all(int(t[1])==0 and int(t[2])==0 for t in totals);observation=not counts;expected=semantic
 ok=code==0 and not timeout and loading and semantic and observation and expected
 row=dict(index=index,block=index//4,configuration=config,executable=str(executable),actual_exit=code,timed_out=timeout,reaped=True,loading_ok=loading,semantic_ok=semantic,observation_ok=observation,passed=ok,totals=totals,sample=samples[0] if samples else None,stages=stages,counts=counts,seconds=time.monotonic()-start)
 records.append(row);(out/'result.json').write_text(json.dumps(row,indent=2)+'\n');(outroot/'results.json').write_text(json.dumps(records,indent=2)+'\n')
 print(json.dumps(dict(index=index,config=config,passed=ok,totals=totals,counts=counts)),flush=True);assert ok,out
for p,h in identity.items():assert sha(p)==h,p
assert subprocess.check_output(['git','diff','--binary'],cwd=R/'krita')==source
(outroot/'identity-final.json').write_text(json.dumps(dict(inputs_verified=True,hashes=identity),indent=2)+'\n')
