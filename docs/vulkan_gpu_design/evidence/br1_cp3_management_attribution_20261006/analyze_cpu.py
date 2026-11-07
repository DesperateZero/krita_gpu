"""Reproduce CPU attribution from xctrace XML, never from wall-thread samples.

Each loop sample belongs to one mechanism and one phase. Inclusive contexts
are a separate view and must not be added to the exclusive mechanism totals.
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import statistics
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
LOOP = 'testSharedBaseline()::$_0::operator()(long long)'
CONTEXTS = {
    'fits_locked': 'KisBackingBudgetController::fitsLocked',
    'control_allocate': 'kisAllocateMutationStorage',
    'storage_owner_allocate': 'KisMutationStorageOwner::allocate',
    'storage_owner_deref': 'KisMutationStorageOwner::deref',
    'provider_adoption': 'KisTiles3PageReplicaProvider::Private::prepareAdoption',
    'provider_prepare_copy': 'KisTiles3PageReplicaProvider::prepareSynchronousWriteCopy',
    'read_link_install': 'KisPageMetadataCoordinator::installCpuReadBinding',
    'read_discovery': 'discoverCpuReadBinding',
    'backing_registration': 'KisPageOwnerLedger::registerBacking',
    'metadata_publication': 'KisPageMetadataCoordinator::preparePublication',
    'canonical_commit': 'KisPageStore::commit',
    'retirement': 'KisPageRetirementQueue::',
}


def binary(frame, resolve):
    node = frame.find('binary')
    return resolve(node).get('name', '') if node is not None else ''


def mechanism(frames, resolve):
    """First specific mechanism from the leaf; allocator heap wins its children.

    Generic atomics, QMutex, tree/vector/hash helpers inherit their nearest
    semantic owner. Thus a mutex below fitsLocked belongs to budget policy,
    and libc malloc below an admitted allocation belongs to physical heap.
    CPU copy is called pixel only with an actual TileData payload-copy caller.
    """
    names = [f.get('name', '') for f in frames]
    if any(binary(f, resolve) == 'libsystem_malloc.dylib' for f in frames):
        return 'physical_heap'
    if names[0].startswith(('_platform_mem', 'memcpy', 'memmove', 'memset', 'memcmp')):
        if any('duplicatePinnedTileData' in n for n in names):
            return 'pixel_copy'
        return 'other_memory_copy'
    for f in frames:
        n = f.get('name', '')
        if n.startswith('KisBackingBudgetController::') or 'processStorageSnapshot()' in n:
            return 'budget_policy_and_ledger'
        if n.startswith(('kisPageStorage', 'kisAllocatePageStorage', 'kisFreePageStorage',
                         'kisAllocatePageProcessStorage', 'kisFreePageProcessStorage')):
            return 'physical_heap'
        if n.startswith(('KisMutationStorageOwner::', 'kisMutationStorageOwner(',
                         'kisAllocateMutationStorage(', 'kisFreeMutationStorage(')):
            return 'storage_owner_and_charge_glue'
        if n.startswith(('KisPageMetadataCoordinator::', 'KisShardSlotIndex<',
                         'KisPageRecordArena', 'KisPageWorkingState::')):
            return 'metadata_and_working_state'
        if n.startswith(('KisTiles3PageReplicaProvider::', 'Tiles3ResidentBinding::',
                         'KisCpuResidentAllocationIndex<', 'KisTileDataStore::',
                         'KisTileData::', 'KisCompletionRegistry::')):
            return 'provider_and_native_lifecycle'
        if n.startswith(('KisPageReadCoordinator::', 'KisCpuReadBindingLink::',
                         'KisCapturedReadView::', 'KisCpuResidentReadPin::')):
            return 'read_view_and_binding'
        if n.startswith('KisPageOwnerLedger::'):
            return 'owner_backing_ledger'
        if n.startswith(('KisPageRetirementQueue::', 'KisPageStoreReclamation',
                         'KisPageRetirementRecord::')) or 'ReclamationExecutor::' in n:
            return 'retirement_and_reclamation'
        if n.startswith(('KisImageEpoch', 'KisRetainedImageEpoch')) or 'resolvePageRoot(' in n:
            return 'epoch_root_and_transaction'
        if n.startswith(('KisPageWriteCoordinator::', 'KisMutationWriteSet::',
                         'KisPageMutationSession::', 'KisPageMutationExecution::',
                         'KisPagePublicationCoordinator::')):
            return 'write_protocol_and_claims'
    return 'adapter_fixture_and_other'


def phase(names):
    # Commit can release a sealed session; seal cleanup nested in commit is
    # still part of commit. Prefer the outer endpoint for this phase view.
    if any('KisPageStore::commit' in n for n in names):
        return 'canonical_commit'
    if any('KisPageMutationSession::sealImpl' in n for n in names):
        return 'seal'
    if any('KisPageMutationSession::beginWriteImpl' in n for n in names):
        return 'page_acquire'
    if any('readResidentPageImpl' in n for n in names):
        return 'before_read'
    return 'adapter_begin_finish_other'


def origin(names):
    for n in names:
        if 'prepareAdoption' in n or 'ResidencyObserver::preparePayload' in n:
            return 'provider_adoption'
        if 'installCpuReadBinding' in n:
            return 'read_link_install'
        if 'preparePublication' in n:
            return 'metadata_publication'
        if 'preparePrivateWrite' in n or 'prepareWriteBaseLocked' in n:
            return 'working_state_prepare'
        if 'prepareWritePlanLocked' in n:
            return 'write_plan'
        if 'CompletionRegistry' in n:
            return 'completion_registry'
        if 'registerBacking' in n or 'prepareBackingChanges' in n:
            return 'owner_backing_ledger'
    return phase(names)


def analyze(path):
    root = ET.parse(path).getroot()
    schema = root.find('.//schema')
    assert schema.get('name') == 'time-profile'
    assert [e.text for e in schema.findall('./col/mnemonic')] == [
        'time', 'thread', 'process', 'core', 'thread-state', 'weight', 'stack']
    ids = {e.get('id'): e for e in root.iter() if e.get('id')}

    def resolve(e):
        return ids[e.get('ref')] if e.get('ref') else e

    totals = Counter()
    groups = Counter()
    phases = Counter()
    inclusive = Counter()
    leaves = Counter()
    backgrounds = Counter()
    charge_origins = defaultdict(Counter)
    phase_mechanisms = defaultdict(Counter)
    mutex_origins = Counter()
    owner_deref_callers = Counter()
    selected_times = []
    all_times = []
    weight_formats = set()
    for row in root.iter('row'):
        cols = [resolve(e) for e in row]
        time, thread, process, core, state, weight, backtrace = cols
        assert state.text == 'Running', state.text
        assert process.find('pid') is not None
        w = int(weight.text)
        weight_formats.add((w, weight.get('fmt')))
        frames = [resolve(f) for f in backtrace]
        names = [f.get('name', '') for f in frames]
        totals['all_weight_ns'] += w
        totals['all_samples'] += 1
        all_times.append(int(time.text))
        if 'Main Thread' not in thread.get('fmt', ''):
            totals['background_weight_ns'] += w
            totals['background_samples'] += 1
            if not frames:
                totals['background_empty_stack_weight_ns'] += w
            for tag, match in CONTEXTS.items():
                if any(match in n for n in names):
                    backgrounds[tag] += w
            continue
        assert frames, 'Empty main-thread stack cannot prove steady-loop membership'
        totals['main_weight_ns'] += w
        totals['main_samples'] += 1
        if not any(LOOP in n for n in names):
            totals['main_outside_loop_weight_ns'] += w
            continue
        totals['loop_weight_ns'] += w
        totals['loop_samples'] += 1
        selected_times.append(int(time.text))
        if re.fullmatch(r'0x[0-9a-fA-F]+', names[0]):
            totals['unsymbolicated_leaf_weight_ns'] += w
        tag = mechanism(frames, resolve)
        endpoint = phase(names)
        groups[tag] += w
        phases[endpoint] += w
        phase_mechanisms[endpoint][tag] += w
        leaves[names[0]] += w
        if tag in ('budget_policy_and_ledger', 'storage_owner_and_charge_glue', 'physical_heap'):
            charge_origins[tag][origin(names)] += w
        for key, match in CONTEXTS.items():
            if any(match in n for n in names):
                inclusive[key] += w
        if names[0] in ('__ulock_wake', '__ulock_wait2'):
            mutex_origins[(names[0], tag)] += w
        if names[0] == 'KisMutationStorageOwner::deref()':
            caller = next((n for n in names[1:] if n.startswith(
                ('KisPage', 'KisImage', 'KisTiled', 'KisTiles'))), 'unknown')
            owner_deref_callers[caller] += w
    assert totals['loop_weight_ns'] == sum(groups.values()) == sum(phases.values())
    assert totals.get('main_outside_loop_weight_ns', 0) == 0
    assert weight_formats == {(1000000, '1.00 ms')}, weight_formats
    result = json.loads((path.parent / 'result.json').read_text())
    assert result['exit_code'] == result['profiler_exit_code'] == 0
    assert result['image_loaded'] and result['actual_init_marker']
    final = json.loads((path.parent / 'identity-final.json').read_text())
    before = json.loads((path.parent / 'identity-before.json').read_text())
    assert final['inputs_verified'] and final['hashes'] == before
    fixture = result['data'][0]
    assert fixture['correctness'] == 'Pass'
    cpu_per_operation_ns = fixture['thread_cpu_ns'] / fixture['completed_operations']
    denominator = totals['loop_weight_ns']

    def attributed(counts):
        return {k: {'weight_ns': v, 'percent': 100 * v / denominator,
                    'approx_cpu_us_per_operation': v / denominator * cpu_per_operation_ns / 1000}
                for k, v in sorted(counts.items(), key=lambda kv: -kv[1])}

    return {
        'record': path.parent.name, 'variant': result['variant'], 'block': result['block'],
        'xml_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'totals': dict(totals),
        'sample_time_ns': [min(all_times), max(all_times)],
        'loop_sample_time_ns': [min(selected_times), max(selected_times)],
        'cpu_us_per_operation_full_fixture': cpu_per_operation_ns / 1000,
        'fixture': fixture,
        'exclusive_mechanisms': attributed(groups),
        'exclusive_phases': attributed(phases),
        'inclusive_contexts_do_not_sum': attributed(inclusive),
        'charge_origin_weight_ns': {k: dict(v) for k, v in charge_origins.items()},
        'phase_mechanism_weight_ns': {k: dict(v) for k, v in phase_mechanisms.items()},
        'background_inclusive_weight_ns_do_not_sum': dict(backgrounds),
        'mutex_leaf_by_mechanism_weight_ns': [
            {'leaf': key[0], 'mechanism': key[1], 'weight_ns': v}
            for key, v in mutex_origins.most_common()],
        'owner_deref_leaf_caller_weight_ns': dict(owner_deref_callers),
        'top_exclusive_leaves': attributed(dict(leaves.most_common(50))),
    }


if __name__ == '__main__':
    records = [analyze(p) for p in sorted(HERE.glob('cpu-*/time-profile.xml'))]
    assert len(records) == 4
    output = {
        'qualification': 'ARM K16 diagnostic CPU localization; not a formal performance gate or causal intervention',
        'weight_semantics': 'time-profile Running rows, 1 ms sample weight; waiting threads disabled in template',
        'approximation': '2 s sampled shares multiplied by whole 6 s loop main-thread CPU/op; assumes stable mix and is not exact per-stage timing',
        'group_rule': 'single nearest semantic mechanism, heap child separated; separate inclusive caller view never summed',
        'records': records,
    }
    (HERE / 'cpu-attribution.json').write_text(json.dumps(output, indent=2) + '\n')
    for variant in ('m5', 'current'):
        selected = [r for r in records if r['variant'] == variant]
        print(variant, 'main CPU us/op', [round(r['cpu_us_per_operation_full_fixture'], 2) for r in selected])
        for field in ('exclusive_mechanisms', 'exclusive_phases'):
            keys = set().union(*(r[field] for r in selected))
            print(field, {k: [round(r[field].get(k, {}).get('percent', 0), 2) for r in selected]
                          for k in sorted(keys)})
