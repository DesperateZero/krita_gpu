"""Running CPU only, exact fixture operation frame, exclusive partition."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,xml.etree.ElementTree as ET
H=Path(__file__).resolve().parent
def mechanism(frames,resolve):
    names=[f.get('name','') for f in frames]
    for f in frames:
        b=f.find('binary')
        if b is not None and resolve(b).get('name')=='libsystem_malloc.dylib':return 'physical_heap'
    if names[0].startswith(('_platform_mem','memcpy','memmove','memset','memcmp')):
        if any('duplicatePinnedTileData' in n for n in names):return 'pixel_before_copy'
        if any('br1TimedOperation' in n for n in names[1:]) and not any('Kis' in n for n in names[1:]):return 'fixture_final_pixels'
        return 'other_memory_copy'
    for n in names:
        if n.startswith('KisBackingBudgetController::') or 'processStorageSnapshot()' in n:return 'budget_policy'
        if n.startswith(('kisPageStorage','kisAllocatePageStorage','kisFreePageStorage','kisAllocatePageProcessStorage','kisFreePageProcessStorage')):return 'physical_heap'
        if n.startswith(('KisMutationStorageOwner::','kisMutationStorageOwner(','kisAllocateMutationStorage(','kisFreeMutationStorage(')):return 'storage_owner_charge'
        if n.startswith(('KisPageMetadataCoordinator::','KisShardSlotIndex<','KisPageRecordArena','KisPageWorkingState::','KisPageStateMachine::')):return 'metadata_working_policy'
        if n.startswith(('KisTiles3PageReplicaProvider::','Tiles3ResidentBinding::','KisCpuResidentAllocationIndex<','KisTileDataStore::','KisTileData::','KisCompletionRegistry::')):return 'provider_payload_lifecycle'
        if n.startswith(('KisPageReadCoordinator::','KisCpuReadBindingLink::','KisCapturedReadView::','KisCpuResidentReadPin::')):return 'read_binding'
        if n.startswith('KisPageOwnerLedger::'):return 'owner_backing_ledger'
        if n.startswith(('KisPageRetirementQueue::','KisPageStoreReclamation','KisPageRetirementRecord::')) or 'ReclamationExecutor::' in n:return 'retirement'
        if n.startswith(('KisImageEpoch','KisRetainedImageEpoch')) or 'resolvePageRoot(' in n:return 'epoch_root_transaction'
        if n.startswith(('KisPageWriteCoordinator::','KisMutationWriteSet::','KisPageMutationSession::','KisPageMutationExecution::','KisPagePublicationCoordinator::')):return 'write_protocol'
    return 'fixture_clock_unclassified'
def analyze(path):
    root=ET.parse(path).getroot();ids={e.get('id'):e for e in root.iter() if e.get('id')}
    def resolve(e):return ids[e.get('ref')] if e.get('ref') else e
    totals=Counter();groups=Counter();phases=Counter();contexts=Counter();leaves=Counter();unknown=Counter()
    for row in root.iter('row'):
        t,thread,process,core,state,weight,backtrace=[resolve(e) for e in row]
        assert state.text=='Running';w=int(weight.text)
        frames=[resolve(f) for f in backtrace];names=[f.get('name','') for f in frames]
        totals['all_samples']+=1;totals['all_weight']+=w
        if 'Main Thread' not in thread.get('fmt',''):
            totals['background_weight']+=w;continue
        totals['main_weight']+=w
        if not any('br1TimedOperation' in n for n in names):
            totals['outside_operation_weight']+=w;continue
        totals['operation_weight']+=w;totals['operation_samples']+=1
        assert names
        if re.fullmatch(r'0x[0-9a-fA-F]+',names[0]):totals['unsymbolicated_leaf_weight']+=w
        g=mechanism(frames,resolve);groups[g]+=w;leaves[names[0]]+=w
        if g=='fixture_clock_unclassified':unknown[' <- '.join(names[:5])]+=w
        if any('KisPageStore::commit' in n or 'KisPageStore::preparedPages' in n for n in names):p='commit'
        elif any('KisPageMutationSession::seal' in n or 'sealMutation' in n for n in names):p='seal'
        elif any('beginWriteImpl' in n or 'KisPageMutationSession::beginWrite' in n for n in names):p='begin_write'
        else:p='begin_pixels_guard_other'
        phases[p]+=w
        matches={'handoff_plan':'prepareWritePlanLocked','fresh_replica':'prepareFreshReplica','private_write':'preparePrivateWrite','private_publish':'publishPrivateWrite',
                 'handoff_accounting':'prepareBackingHandoff','joint_metadata_install':'installRecoverableWrite','provider_duplicate':'duplicatePinnedTileData','budget':'fitsMetadataStorageLocked'}
        for tag,match in matches.items():
            if any(match in n for n in names):contexts[tag]+=w
        if any('prepareWritePlanLocked' in n for n in names) and any('preparePublicationImpl' in n or 'prepareRecoverableWrite' in n for n in names):contexts['handoff_metadata_prepare']+=w
    assert totals['operation_samples']>0
    assert sum(groups.values())==sum(phases.values())==totals['operation_weight']
    result=json.loads((path.parent/'result.json').read_text());scale=result['cpu_ns_per_op']/1000/totals['operation_weight']
    def values(c):return {k:{'weight_ns':v,'share':v/totals['operation_weight'],'approx_cpu_us':v*scale} for k,v in c.most_common()}
    return {'record':path.parent.name,'variant':result['variant'],'block':result['block'],'cpu_us':result['cpu_ns_per_op']/1000,'wall_us':result['wall_ns_per_op']/1000,'totals':dict(totals),
            'exclusive_mechanisms':values(groups),'exclusive_phases':values(phases),'inclusive_contexts_do_not_sum':values(contexts),'top_leaves':values(Counter(dict(leaves.most_common(35)))),'unclassified_stacks':dict(unknown),'xml_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
assert json.loads((H/'profile-identity-final.json').read_text())['inputs_verified']
records=[analyze(p) for p in sorted(H.glob('cpu-*/time-profile.xml'))];assert len(records)==6
out={'method':'3s Running CPU samples within noinline exact operation; shares scaled by whole15s operation CPU/op. Descriptive localization, no lower bound or causal per-function price. Background/setup/validation/drain excluded from operation and counted separately.','records':records,'analysis_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(H/'cpu-summary.json').write_text(json.dumps(out,indent=2)+'\n')
for r in records:
    print(r['record'],'cpu/wall',round(r['cpu_us'],2),round(r['wall_us'],2),'samples',r['totals']['operation_samples'])
    for field in ['exclusive_mechanisms','exclusive_phases','inclusive_contexts_do_not_sum']:print(field,{k:round(v['approx_cpu_us'],2) for k,v in r[field].items()})
