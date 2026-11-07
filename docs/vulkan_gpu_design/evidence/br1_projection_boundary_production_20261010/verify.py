#!/usr/bin/env python3
import hashlib,json,re,shutil,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];P=R/'krita';B=P/'_build-br0-cpu'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
parent='c13c44249338bf10477b9b07c65726e5933e51f9'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip()
assert head.startswith('8198c36ed7')
assert not subprocess.check_output(['git','status','--porcelain','-uno'],cwd=P,text=True).strip()
diff=subprocess.check_output(['git','diff','--binary',parent,head],cwd=P)
assert diff==(H/'confirm-r1/source.diff').read_bytes()
(H/'production.diff').write_bytes(diff)
files=subprocess.check_output(['git','diff','--name-only',parent,head],cwd=P,text=True).splitlines()
source={}
for f in files:
 for kind,data in [('source', (P/f).read_bytes()),('parent-source',subprocess.check_output(['git','show',f'{parent}:{f}'],cwd=P))]:
  dest=H/kind/f;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 source[f]=sha(P/f)
(H/'candidate-r1').mkdir(exist_ok=True)
shutil.copy2(B/'bin/libkritaimage.21.0.0.dylib',H/'candidate-r1/libkritaimage.21.0.0.dylib')
(H/'executables').mkdir(exist_ok=True)
for t in ['kis_painter_test','kis_async_merger_test','kis_projection_test','kis_tiled_data_manager_test']:
 shutil.copy2(B/'bin'/t,H/'executables'/t)
fixture=H.parent/'br1_upstream_cost_accounting_20261007/fixture-current/probe'
shutil.copy2(fixture,H/'executables/probe')
shutil.copy2(B/'CMakeCache.txt',H/'CMakeCache.txt')
# Capture only relevant compile rows; observer commands retain the actual complete link.
rows=json.loads((B/'compile_commands.json').read_text())
(H/'compile-commands.json').write_text(json.dumps([x for x in rows if x['file'] in {str(P/f) for f in files}],indent=2)+'\n')
libhash={c:sha(H/c/'libkritaimage.21.0.0.dylib') for c in ['parent-lib','candidate-r0','candidate-r1']}
results={}
for batch,expected in [('tests-r1',4),('tests-x86-r1',4),('capability-r1',4),('confirm',64),('confirm-r1',64)]:
 rows=json.loads((H/batch/'results.json').read_text());assert len(rows)==expected and all(r['passed'] for r in rows)
 assert json.loads((H/batch/'identity-final.json').read_text())['inputs_verified']
 count=sum(int(t[0]) for r in rows for t in r['totals']);results[batch]={'processes':len(rows),'passed':count,'failed':0,'skipped':0}
 for row in rows:
  runtime=json.loads((H/batch/f"{row['index']:02}-{row['configuration']}"/'runtime.json').read_text())
  actual=[v for p,v in runtime.items() if 'libkritaimage.' in p];assert len(actual)==1
  if batch=='confirm':assert actual[0]==libhash['parent-lib' if row['configuration']=='parent' else 'candidate-r0']
  elif batch=='confirm-r1' or batch.startswith('tests'):assert actual[0]==libhash['parent-lib' if row['configuration']=='parent' else 'candidate-r1']
  if batch=='confirm-r1' or batch.startswith('tests'):
   for p,h in runtime.items():assert sha(p)==h,p
summary=json.loads((H/'summary-r1.json').read_text());assert summary['incremental_value_passed'] and summary['same_runtime_dependencies']
for r in summary['mechanisms']:
 if r['stage']!=2:continue
 fused=r['configuration']=='candidate-count'
 assert r['merge']==19 and r['pixel_operations']==19
 assert r['fill_operations']==(0 if fused else 13) and r['accepted_cold_plans']==(96 if fused else 132)
 assert r['new_batches']==r['successful_seals']==(19 if fused else 32)
 if fused:assert r['fused_clear']==13 and r['failed_fusion']==0 and r['initialized_bytes']==566464
# Original proof machinery is unchanged; only the friend strategy seam is new.
assert all(not f.startswith('libs/image/pagestore/') and f!='libs/image/tiles3/kis_tiled_data_manager.cc' for f in files)
for f in files:
 if '/tests/' not in f:
  text=(P/f).read_text();assert 'br1_boundary_' not in text and 'BR1_BOUNDARY_' not in text
assert (H/'run-r0.py').read_bytes() and sha(H/'run-r0.py')==json.loads((H/'confirm/identity-before.json').read_text())[str(H/'run.py')]
assert sha(H/'run.py')==json.loads((H/'confirm-r1/identity-before.json').read_text())[str(H/'run.py')]
# The live responsibility matrix is frozen here as well as maintained at its one active path.
shutil.copy2(H.parent/'br1_projection_boundary_trial_20261010/BOUNDARY_PLAN.md',H/'BOUNDARY_PLAN-snapshot.md')
result=dict(parent=parent,product=head,source_commit_matches_tested_patch=True,product_tracked_clean=True,source_files=source,library_sha256=libhash,results=results,production_has_no_prototype_hooks=True,original_pagestore_policy_unchanged=True,primary_value_passed=True,strict_stage_noninferiority_proven=False,m6_promoted=False,source_identity_note='Compiled/tested dirty source equals committed source byte-for-byte; generated build identity is frozen separately, no post-commit rebuild claimed.')
(H/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
