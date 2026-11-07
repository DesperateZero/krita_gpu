#!/usr/bin/env python3
"""Symmetric correction of frozen profiles; no new measurement or sample filtering."""
import hashlib,json,statistics,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];frozen='--frozen' in sys.argv
P=H/'raw-input/business' if frozen else H.parent/'br1_business_cost_localization_20261007'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
if frozen:
    for name,digest in load(H/'input-fingerprints.json').items():assert sha(H/name)==digest
manifest={e['path']:e for e in load(P/'raw-manifest.json')['members']}
meta=load(P/'profile-results.json');records=[];identities={}
assert sha(P/'profile-results.json')==manifest['profile-results.json']['sha256']
inputs=[P/'raw-manifest.json',P/'profile-results.json']
management={'adapter_manager','provider_ledger_completion','mutation_publication','budget_storage','metadata','retirement','read_binding','epoch'}
for row in meta:
    folder=P/f"profile-{row['index']:02}-{row['side']}";path=folder/'selected-stacks.json'
    relative=str(path.relative_to(P));assert sha(path)==manifest[relative]['sha256']
    inputs.append(path)
    identities[str(path)]=sha(path);samples=[s for s in load(path) if s['phase']=='Stroke']
    counts=Counter();changes=Counter();actors=defaultdict(Counter);examples=[];management_leaves=Counter();leaf_examples=Counter()
    for sample in samples:
        old=sample['mechanism'];new=old
        for frame in sample['frames']:
            if any(token in frame for token in ['KoStreamedMath<','OverCompositor32<','KoCompositeOp','KoOptimizedComposite']):
                new='pixel_brush';break
            if frame.startswith(('KisPage','KisTiledDataManager','KisCpu','KisMutation','KisBacking','KisTiles3','Tiles3Resident','KisCompletion')):break
        counts[new]+=1;actors[sample['actor']][new]+=1
        if new in management:
            leaf=sample['frames'][0];leaf_examples[leaf]+=1
            if any(t in leaf for t in ['memcpy','memmove','memset','fillWithPixel']):kind='copy_fill_leaf'
            elif any(t in leaf for t in ['__ulock_','__psynch_','QMutex','QBasicMutex','QReadWriteLock','QWaitCondition']):kind='synchronization_primitive_leaf'
            else:kind='other_protocol_leaf'
            management_leaves[kind]+=1
        if new!=old:
            changes[f'{old} -> {new}']+=1
            if len(examples)<3:examples.append(dict(old=old,new=new,frames=sample['frames'][:9]))
    assert sum(counts.values())==len(samples)
    partition=dict(pixel=counts['pixel_brush'],management=sum(counts[k] for k in management),
        heap=counts['physical_heap'],other=counts['other'])
    assert sum(partition.values())==len(samples)
    records.append(dict(index=row['index'],side=row['side'],total=len(samples),partition=partition,
        corrected_mechanisms=dict(counts),reclassifications=dict(changes),actors={a:dict(c) for a,c in actors.items()},
        management_leaf_partition=dict(management_leaves),management_top_leaves=leaf_examples.most_common(12),
        projection_update_distribution=dict(Counter(s['projection_updates'] for s in row['samples'])),
        original_semantic_replays=len(row['samples']),examples=examples))
means={side:{k:statistics.mean(r['partition'][k] for r in records if r['side']==side) for k in ['pixel','management','heap','other']}
    for side in ['current','upstream']}
difference={k:means['current'][k]-means['upstream'][k] for k in means['current']};total=sum(difference.values())
summary=dict(records=records,means=means,sample_difference=difference,total_sample_difference=total,
    descriptive_management_share_of_sample_difference=difference['management']/total,
    interpretation='Exclusive Running sample contexts over equal64 replay counts. Management protocol contexts include inner copy/fill and synchronization primitives; they are not pure control overhead. The additional leaf partition is descriptive, not a CPU/wait accounting. No conversion to wall, causal/removable percent, strict bound or CI. Current profile source predates 2f22452e2d. One current replay has18 updates; others19. No samples excluded.',
    previous_classification_correction='117/106 current samples were actual inner pixel kernels masked by the outer adapter symbol; upstream6/5 samples also corrected symmetrically. Actor totals and original timing intervals unchanged.',
    new_benchmark_processes=0,new_production_changes=0,new_formal_m6_passes=0)
(H/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
source_paths=[
    'libs/image/kis_painter_blt_multi_fixed.cpp','libs/image/kis_painter.cc',
    'libs/image/tiles3/kis_tiled_data_manager.cc','libs/image/tiles3/kis_random_accessor.cc','libs/image/tiles3/kis_tile.cc',
    'libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp','libs/image/pagestore/KisPageStore.cpp',
    'libs/image/pagestore/KisPageSnapshotArray_p.h','libs/image/pagestore/KisTiles3PageReplicaProvider.cpp']
for side,root in [('current',R/'krita'),('upstream',R/'build/br1-cp0-20261003/upstream-source')]:
    if frozen:continue
    for name in source_paths:
        path=root/name
        if not path.exists():continue
        identities[str(path)]=sha(path)
        copy=H/'source-snapshot'/side/name;copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(path.read_bytes())
projection_path=H/'raw-input/results-v3.json' if frozen else H.parent/'br1_projection_redundancy_20261007/results-v3.json'
projection_manifest=H/'raw-input/projection-raw-manifest.json' if frozen else projection_path.parent/'raw-manifest.json'
expected_projection=next(e['sha256'] for e in load(projection_manifest)['members'] if e['path']=='results-v3.json')
assert sha(projection_path)==expected_projection
projection=load(projection_path);range_reports=[]
for r in projection:
    if not r['events']:continue
    groups=defaultdict(list)
    for e in r['events']:
        if e['merge']<=19 and e['phase']=='composite' and e['event']=='targets':groups[(e['merge'],e['operation'])].append(tuple(e['page']))
    range_reports.append(dict(index=r['index'],scopes=len(groups),declared_page_visits=sum(map(len,groups.values())),
        row_order_incompatible_with_column_order=sum(p!=sorted(p) for p in groups.values())))
(H/'range-order-audit.json').write_text(json.dumps(dict(records=range_reports,
    interpretation='11/19 observed root composite ranges differ from borrowExecution column-major input. Code also uses non-const range iteration over a shared array, triggering detach even for a canonical nonempty input. These are examples of representation churn, not priced root causes or justification for isolated patches.'),indent=2)+'\n')
if not frozen:
    for path in inputs:
        identities[str(path)]=sha(path)
        copy=H/'raw-input/business'/path.relative_to(P);copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(path.read_bytes())
    identities[str(projection_path)]=sha(projection_path)
    identities[str(projection_manifest)]=sha(projection_manifest)
    (H/'raw-input/results-v3.json').write_bytes(projection_path.read_bytes())
    (H/'raw-input/projection-raw-manifest.json').write_bytes(projection_manifest.read_bytes())
    (H/'input-fingerprints.json').write_text(json.dumps({str(p.relative_to(H)):sha(p) for p in sorted((H/'raw-input').rglob('*')) if p.is_file()},indent=2)+'\n')
    (H/'identity.json').write_text(json.dumps(dict(product=subprocess.check_output(['git','-C',str(R/'krita'),'rev-parse','HEAD'],text=True).strip(),
        outer_parent=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),
        upstream='9a24ae0d8c070884fb013594191002e1a1b39a19',
        profiled_product='128fb32a71fef69f462da2c2dfa8d187ed94db52',
        profiled_production_equivalent='38834c4e2612c819f9d088dfd59c59889f295a49',hashes=identities,
        frozen_profile_manifest_sha256=sha(P/'raw-manifest.json')),indent=2)+'\n')
print(json.dumps(dict(means=means,difference=difference,descriptive_management_share=difference['management']/total)))
