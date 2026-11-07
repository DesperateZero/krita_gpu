#!/usr/bin/env python3
"""Verify the qualified source/build, archived originals and active entry links."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
HERE=Path(__file__).resolve().parent
DESIGN=HERE.parents[1]; ROOT=DESIGN.parents[1]; SOURCE=ROOT/'krita'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip()
assert revision=='5173c807c87bb1619325249a07a8b4f4f8f09f09'
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=SOURCE,text=True)
identity=json.loads((HERE/'correctness-final/identity.json').read_text())
assert identity['source_revision']==revision
for name,record in identity['files'].items(): assert sha(Path(name))==record['sha256'],name
matrix=json.loads((HERE/'correctness-final/manifest.json').read_text())
assert len(matrix)==20 and all(r['returncode']==0 and r['totals'][1]=='0' for r in matrix)
vk=json.loads((HERE/'correctness-final/vulkan-manifest.json').read_text())
assert len(vk)==2 and all(r['returncode']==0 and r['totals'][0][1]=='0' for r in vk)
for r in vk: assert sha(Path(r['command'][-1]))==r['binary_sha256']
for arch in ('arm64','x86_64'):
    probe=json.loads((HERE/f'install-{arch}-final-identity.json').read_text())
    assert probe['source_revision']==revision and probe['returncode']==0 and not probe['tracked_diff']
    for name,digest in probe['hashes'].items(): assert sha(Path(name))==digest,name
    assert 'all_checks_passed=1' in (HERE/f'install-{arch}-final.log').read_text()
perf=json.loads((HERE/'repair-performance-analysis.json').read_text());assert perf['result']=='Pass'
perfidentity=json.loads((HERE/'repair-runtime-identity.json').read_text())
for r in perfidentity['runtimes'].values(): assert sha(Path(r['directory'])/'libkritaimage.21.0.0.dylib')==r['libkritaimage_sha256']
archive=DESIGN/'archive/br1_pre_m6_20260925'
manifest=json.loads((archive/'manifest.json').read_text());assert len(manifest['documents'])==45
for r in manifest['documents']:
    body=(DESIGN/r['path']).read_bytes()[r['notice_bytes']:]
    assert hashlib.sha256(body).hexdigest()==r['original_sha256'],r['path']
for name,r in json.loads((archive/'previous-entry-snapshots.json').read_text()).items():
    assert hashlib.sha256(r['text'].encode()).hexdigest()==r['sha256'],name
active=[DESIGN/'README.md',DESIGN/'00_status_and_mvp_contract.md',DESIGN/'31_p0_reset_and_execution_sequence.md',DESIGN/'92_br1_m6_m8_execution_baseline.md',archive/'README.md',HERE/'README.md']
for path in active:
    for href in re.findall(r'\]\(([^)]+)\)',path.read_text()):
        if re.match(r'^(https?:|#)',href): continue
        target=href.split('#')[0].split(':')[0]
        assert (path.parent/target).exists(),(path,href)
# Same selector source, including all miss/validation branches, as the
# previously adopted matched-control production revision.
selector='libs/image/pagestore/KisPageWriteCoordinator.cpp'
old=subprocess.check_output(['git','show','095193d11a:'+selector],cwd=SOURCE,text=True)
new=(SOURCE/selector).read_text()
def select_body(s):
    a=s.index('KisPageWritePlanKind KisPageWriteCoordinator::select(')
    start=s.index('{',a);depth=1;i=start+1
    while depth:
        if s[i]=='{':depth+=1
        elif s[i]=='}':depth-=1
        i+=1
    return s[a:i]
assert select_body(old)==select_body(new)
result={'source_revision':revision,'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
'cpu_passed':sum(int(r['totals'][0]) for r in matrix),'vulkan_foundation_passed':sum(int(r['totals'][0][0]) for r in vk),
'current_build_identity_mismatches':[],'allocator_architectures':['arm64','x86_64'],'archive_count':45,'archive_body_mismatches':[],
'active_link_path_mismatches':[],'selector_source_equal_to':'095193d11a','selector_source_sha256':hashlib.sha256(select_body(new).encode()).hexdigest(),
'performance_result':perf['result'],'qualification':'M5 repair baseline qualifies M6 entry only. M6/M7/M8 and formal BR1-PERF remain open.'}
(HERE/'final-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
