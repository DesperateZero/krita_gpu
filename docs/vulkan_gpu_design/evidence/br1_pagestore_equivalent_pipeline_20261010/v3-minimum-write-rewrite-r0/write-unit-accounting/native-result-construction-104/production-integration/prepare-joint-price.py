from pathlib import Path
import json,subprocess,hashlib,itertools
p=Path(__file__).resolve().parent;r=p.parents[1];old=r/'build/br1-minimum-write-rewrite/native-result-104';u=old.parent/'native-result-104-m1m5';out=p/'joint-price';out.mkdir(exist_ok=True)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
def put(n,v):(out/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
variants={'P':(r/'krita',old.parent/'seal-closure-98/N'), 'U':(u/'source',u/'build/bin'), 'N':(p/'source',p/'build/bin')}
expected='214f3302a3551c9ef2270fd4823808c500b320217ae9621689ca7004ab8f066d';assert sha(variants['P'][1]/'libkritaimage.21.0.0.dylib')==expected
identities={}
for tag,(source,lib) in variants.items():
 args=json.loads((old/'price-compile-R.command.json').read_text());args=[a.replace(str(old/'source'),str(source)).replace(str(old/'price-R'),str(out/('price-'+tag))) for a in args]
 put('compile-'+tag+'.json',args)
 with (out/('compile-'+tag+'.log')).open('w') as f:subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True)
 args=json.loads((old/'price-link-R.command.json').read_text());args=[a.replace(str(old/'price-R'),str(out/('price-'+tag))) for a in args];args=[str(lib/'libkritaimage.21.0.0.dylib') if 'lifetime-protocol-100-principle/N/libkritaimage' in a else a for a in args]
 put('link-'+tag+'.json',args)
 with (out/('link-'+tag+'.log')).open('w') as f:subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True)
 identities[tag]={'source':str(source),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),'library':str(lib/'libkritaimage.21.0.0.dylib'),'library_sha256':sha(lib/'libkritaimage.21.0.0.dylib'),'binary':str(out/('price-'+tag)),'binary_sha256':sha(out/('price-'+tag))}
# Protected Fresh comparison uses the same public benchmark source and product headers.
args=json.loads((u/'fresh-R-compile.command.json').read_text());args=[a.replace(str(old/'source'),str(r/'krita')).replace(str(u/'fresh-R'),str(out/'fresh-P')) for a in args]
put('fresh-P-compile.json',args)
with (out/'fresh-P-compile.log').open('w') as f:subprocess.run(args,cwd=u/'build',stdout=f,stderr=subprocess.STDOUT,check=True)
args=json.loads((u/'fresh-R-link.command.json').read_text());args=[a.replace(str(u/'fresh-R'),str(out/'fresh-P')) for a in args];args=[str(variants['P'][1]/'libkritaimage.21.0.0.dylib') if 'lifetime-protocol-100-principle/N/libkritaimage' in a else a for a in args]
put('fresh-P-link.json',args)
with (out/'fresh-P-link.log').open('w') as f:subprocess.run(args,cwd=u/'build',stdout=f,stderr=subprocess.STDOUT,check=True)
put('IDENTITIES.json',identities)
jobs=[]
for block,order in enumerate([('P','U','N'),('N','U','P')]):
 for case in [3,7]:
  for tag in order:jobs.append(dict(block=block,case=case,mode=2,tag=tag))
put('CALIBRATION_PROTOCOL.json',{'jobs':jobs,'stop':'12 fixed processes; no replacement; calibration is post-implementation reference, not prior forecast'})
jobs=[]
for block,order in enumerate(list(itertools.permutations(['P','U','N']))*2):
 for case in [3,7]:
  for mode in [0,2]:
   for tag in order:jobs.append(dict(block=block,case=case,mode=mode,tag=tag))
checks=[]
for case in [3,7]:
 for mode in [0,2]:
  actual=[tuple(j['tag'] for j in jobs if j['block']==b and j['case']==case and j['mode']==mode) for b in range(12)]
  assert all(actual.count(o)==2 for o in itertools.permutations(['P','U','N']))
  for a,b in [('P','N'),('U','N'),('P','U')]:
   counts=[sum(o.index(a)<o.index(b) for o in actual),sum(o.index(b)<o.index(a) for o in actual)]
   assert counts==[6,6];checks.append(dict(case=case,mode=mode,pair=[a,b],orientation=counts))
put('VALIDATION_PROTOCOL.json',{'jobs':jobs,'order_assertions':checks,'source_workload_sha256':sha(old/'price.cpp'),'stop':'144 fixed processes/12 triad blocks; no optional stopping, retain original failures, no sample replacement','forecast_sha256':None,'endpoint':'4 lifetimes, 16 warm writes of 16 pages, read after each, real H1 undo/redo, manager destruction and standard drain. P actual48c89, U completed10 prototype, N integrated production candidate. CPU mode0, instructions mode2 separate.'})
jobs=[]
for block in range(20):
 for bucket in ['write-n64-k1-b4','write-n1024-k16-b4']:
  for pair,order in enumerate([['P','N'],['N','P']]):
   for tag in order:jobs.append(dict(block=block,pair=pair,bucket=bucket,tag=tag))
for bucket in ['write-n64-k1-b4','write-n1024-k16-b4']:
 orders=[tuple(j['tag'] for j in jobs if j['bucket']==bucket and j['block']==b and j['pair']==pair) for b in range(20) for pair in range(2)]
 assert orders.count(('P','N'))==20 and orders.count(('N','P'))==20
put('FRESH_PROTOCOL.json',{'jobs':jobs,'rate_ms':750,'stop':'160 fixed processes/40 pairs per bucket,20 order-balanced blocks; no replacements or optional stopping','confidence':'Median block N/P throughput, one-sided97.5% bootstrap lower per bucket >=0.98,50000 resamples seed260926; familywise95%','scope':'N forced-Fresh native path vs P actual48c89 ordinary legal reuse; same public partial-write H0 workload. Conservative replacement control, not historical selector-only/M6/upstream qualification'})
print('Built identical public workload P/U/N and P Fresh, protocols generated; 0 target performance launches',flush=True)
