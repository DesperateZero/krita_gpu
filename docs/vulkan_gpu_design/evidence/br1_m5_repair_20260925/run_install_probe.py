#!/usr/bin/env python3
import hashlib,json,os,pathlib,re,shlex,subprocess,sys
here=pathlib.Path(__file__).resolve().parent
root=here.parents[3]/'krita'; build=root/'_build-br0-cpu'
out=pathlib.Path('/tmp/codex-br1-m5-repaired-install');out.mkdir(exist_ok=True)
arch=sys.argv[1] if len(sys.argv)>1 else 'arm64'
tag=sys.argv[2] if len(sys.argv)>2 else 'initial'
log=here/f'install-{arch}-{tag}.log'
if log.exists(): raise RuntimeError(f'refusing to overwrite {log}')
rec=next(c for c in json.loads((build/'compile_commands.json').read_text()) if c['file'].endswith('/KisPageStoreCpuMutationTest.cpp'))
args=shlex.split(rec['command']); flags=[];i=0
while i<len(args):
    if args[i] in ('-o','-c','-arch'): i+=2;continue
    flags.append(args[i]);i+=1
source=here/'install-allocation-probe.cpp';obj=out/f'{arch}.o';binary=out/f'probe-{arch}';lib=out/f'interposer-{arch}.dylib'
commands=[['clang++','-std=c++17','-dynamiclib','-arch',arch,str(here/'allocation-interposer.cpp'),'-o',str(lib)],flags+['-arch',arch,'-c',str(source),'-o',str(obj)]]
section=(build/'build.ninja').read_text().split('build bin/KisPageStoreCpuMutationTest:')[1].split('\n\n')[0]
libs=re.search(r'^  LINK_LIBRARIES = (.*)$',section,re.M).group(1)
commands.append([args[0],'-arch',arch,str(obj),str(lib),'-o',str(binary),'-F'+str(root/'_install/lib')]+shlex.split(libs))
for cmd in commands: subprocess.run(cmd,cwd=build,check=True)
env=os.environ.copy();env.update(QT_QPA_PLATFORM='offscreen',QT_HASH_SEED='0',DYLD_INSERT_LIBRARIES=str(lib))
cmd=['arch','-'+arch,str(binary)]
r=subprocess.run(cmd,cwd=build,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
log.write_text(r.stdout)
identity={'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'tracked_diff':subprocess.check_output(['git','diff'],cwd=root,text=True),'compile_link_commands':commands,'run':cmd,'environment':{k:env[k] for k in ('QT_QPA_PLATFORM','QT_HASH_SEED','DYLD_INSERT_LIBRARIES')},'returncode':r.returncode,'hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (source,here/'allocation-interposer.cpp',binary,lib,build/'bin/libkritaimage.21.0.0.dylib')}}
(here/f'install-{arch}-{tag}-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
print(r.stdout,end='');sys.exit(r.returncode)
