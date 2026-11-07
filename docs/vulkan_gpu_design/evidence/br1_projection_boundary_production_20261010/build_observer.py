#!/usr/bin/env python3
"""Observation-only derived library; no alternative policy, pixel code or owners."""
import difflib,hashlib,json,shlex,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];P=R/'krita';B=P/'_build-br0-cpu';O=H/'observed-r1'
O.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
(O/'observe.h').write_text('''#pragma once
#include <cstdint>
void br1_note(unsigned, std::uint64_t=1);
struct Br1Scope {bool previous; Br1Scope(); ~Br1Scope();};
''')
(O/'observe.cpp').write_text('''#include "observe.h"
#include <atomic>
#include <cstdio>
namespace {std::atomic<unsigned> stage{0}; std::atomic<std::uint64_t> counts[6][12]{}; thread_local bool inside=false;}
void br1_note(unsigned i,std::uint64_t n){if(inside)counts[stage.load(std::memory_order_relaxed)%6][i].fetch_add(n,std::memory_order_relaxed);}
Br1Scope::Br1Scope():previous(inside){inside=true;br1_note(0);}
Br1Scope::~Br1Scope(){inside=previous;}
extern "C" __attribute__((visibility("default"))) void br1_cost_stage(int n){stage.store(n,std::memory_order_relaxed);}
extern "C" __attribute__((visibility("default"))) void br1_cost_dump(){for(unsigned s=0;s<6;++s){std::fprintf(stderr,"BR1_BOUNDARY_COUNT {\\"stage\\":%u,\\"values\\":[",s);for(unsigned i=0;i<12;++i)std::fprintf(stderr,"%s%llu",i?",":"",(unsigned long long)counts[s][i].load());std::fprintf(stderr,"]}\\n");}}
''')
changes={
 'kis_async_merger.cpp': [('    KisMergeWalker::LeafStack &leafStack = walker.leafStack();','    Br1Scope observation;\n    KisMergeWalker::LeafStack &leafStack = walker.leafStack();')],
 'kis_painter.cc': [('    bool entered = false;','    br1_note(1);\n    bool entered = false;'),('    if (painted) return;','    if (painted) {br1_note(3);return;}\n    br1_note(4);'),('                memset(bytes, 0, size_t(columns) * d->device->pixelSize());','                br1_note(5, size_t(columns) * d->device->pixelSize());\n                memset(bytes, 0, size_t(columns) * d->device->pixelSize());')],
 'pagestore/KisPageStore.cpp':[('        const auto source = acquire.source;','        br1_note(8);\n        const auto source = acquire.source;')],
 'pagestore/KisTiledDataManagerPageStoreBackend.cpp':[
 ('    return batch;\n}\ncatch (const std::bad_alloc &)','    br1_note(9);\n    return batch;\n}\ncatch (const std::bad_alloc &)'),
 ('    if (!sealed) {','    if(sealed)br1_note(10);\n    if (!sealed) {'),
 ('    if (changed) changed->clear();\n    if (delivery && !delivery->isEmpty()) {\n        KisPageStoreDetail::setError(error, QStringLiteral("adapter delivery output is already occupied"));\n        return false;','    br1_note(7);\n    if (changed) changed->clear();\n    if (delivery && !delivery->isEmpty()) {\n        KisPageStoreDetail::setError(error, QStringLiteral("adapter delivery output is already occupied"));\n        return false;'),
 ('    if (!committed.isValid()) pageStore->abort(transaction);','    if(committed.isValid())br1_note(11);\n    if (!committed.isValid()) pageStore->abort(transaction);')]
}
commands=[];replaced={};identity={};rows=json.loads((B/'compile_commands.json').read_text())
for name,replacements in changes.items():
 source=P/'libs/image'/name;original=source.read_text();t=original
 for a,b in replacements:assert t.count(a)==1,(name,a,t.count(a));t=t.replace(a,b)
 if name.endswith('Backend.cpp'):
  start=t.index('KisPageStoreWriteOperationResult KisTiledDataManagerPageStoreBackend::runCpuMutationOperation(');end=t.index('\nKisPageStoreWriteOperationResult KisTiledDataManagerPageStoreBackend::writeOperation(',start)
  body=t[start:end];assert body.count('    using Result = KisPageStoreWriteOperationResult;')==1
  body=body.replace('    using Result = KisPageStoreWriteOperationResult;','    br1_note(6);\n    using Result = KisPageStoreWriteOperationResult;');t=t[:start]+body+t[end:]
 t='#include "observe.h"\n'+t;target=O/source.name;target.write_text(t)
 (O/(source.name+'.diff')).write_text(''.join(difflib.unified_diff(original.splitlines(True),t.splitlines(True),fromfile=str(source),tofile=str(target))))
 cmd=shlex.split(next(x['command'] for x in rows if x['file']==str(source)));old=cmd[cmd.index('-o')+1];obj=str(O/(source.name+'.o'))
 cmd[cmd.index('-o')+1]=obj;cmd[cmd.index('-c')+1]=str(target);cmd+=['-I'+str(source.parent),'-I'+str(O)];commands.append(cmd);replaced[old]=obj;identity[str(source)]=sha(source)
probe=commands[0].copy();probe[probe.index('-o')+1]=str(O/'observe.o');probe[probe.index('-c')+1]=str(O/'observe.cpp');commands.append(probe)
raw=subprocess.check_output([str(R/'.venv/bin/ninja'),'-C',str(B),'-t','commands','kritaimage'],text=True)
tokens=shlex.split(next(x for x in reversed(raw.splitlines()) if ' -dynamiclib ' in x));a=next(i for i,x in enumerate(tokens) if x.endswith(('/clang++','/c++')));b=tokens.index('&&',a) if '&&' in tokens[a:] else len(tokens)
link=[replaced.get(x,x) for x in tokens[a:b]];link[link.index('-o')+1]=str(O/'libkritaimage.21.0.0.dylib');link.append(str(O/'observe.o'));commands.append(link)
(O/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
for i,cmd in enumerate(commands):
 print('compile/link',i,flush=True)
 with (O/f'build-{i}.log').open('x') as log:subprocess.run(cmd,cwd=B,stdout=log,stderr=subprocess.STDOUT,check=True)
(O/'libkritaimage.21.dylib').symlink_to('libkritaimage.21.0.0.dylib')
for p in list(O.iterdir())+[Path(__file__),B/'bin/libkritaimage.21.0.0.dylib',B/'compile_commands.json',B/'CMakeCache.txt']+[Path(x) if Path(x).is_absolute() else B/x for x in link if x.endswith('.o')]:
 if p.is_file():identity[str(p)]=sha(p)
(H/'observer-r1-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
