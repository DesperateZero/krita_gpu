from pathlib import Path
from collections import Counter
import hashlib,json,xml.etree.ElementTree as ET
H=Path(__file__).resolve().parent;D=H.parent/'br1_m6_calibration_resolution_20261006'
def analyze(path):
 root=ET.parse(path).getroot();ids={e.get('id'):e for e in root.iter() if e.get('id')}
 def resolve(e):return ids[e.get('ref')] if e.get('ref') else e
 totals=Counter();cores=Counter();opcores=Counter();leaves=Counter();phases=Counter();mechanisms=Counter()
 for row in root.iter('row'):
  t,thread,process,core,state,weight,bt=[resolve(e) for e in row]
  totals['all_samples']+=1
  if state.text!='Running':totals['not_running_samples']+=1;continue
  totals['running_samples']+=1;cores[core.get('fmt','')]+=1
  if 'Main Thread' not in thread.get('fmt',''):totals['background_running_samples']+=1;continue
  totals['main_running_samples']+=1
  frames=[resolve(e) for e in bt];names=[f.get('name','') for f in frames]
  apis=['KisPageStore::beginCurrentTransaction','KisPageStore::beginMutation','KisPageMutationSession::beginWrite',
   'KisPageMutationSession::seal','KisPageStore::preparedPages','KisPageStore::commit']
  operation=any(any(n.startswith(api) for api in apis) for n in names)
  for f in frames:
   source=f.find('source')
   if source is not None and source.find('path') is not None:
    p=resolve(source.find('path')).text
    if p==str(D/'baseline-seed.cpp') and 158<=int(source.get('line','0'))<=171:operation=True
  if not operation:totals['outside_operation_main_samples']+=1;continue
  totals['operation_samples']+=1;opcores[core.get('fmt','')]+=1;leaves[names[0]]+=1
  phase='commit' if any(n.startswith(('KisPageStore::commit','KisPageStore::preparedPages')) for n in names) else \
   'seal' if any('KisPageMutationSession::seal' in n or 'sealMutation' in n for n in names) else \
   'begin_write' if any('beginWrite' in n for n in names) else 'begin_pixels_guard_other'
  phases[phase]+=1;category=None
  for f in frames:
   b=f.find('binary')
   if b is not None and resolve(b).get('name')=='libsystem_malloc.dylib':category='physical_heap';break
  for n in names:
   if category:break
   if n.startswith(('KisBackingBudgetController::','KisBackingBudgetReservation::')):category='budget_policy'
   elif n.startswith(('kisPageStorage','kisAllocatePageStorage','kisFreePageStorage','KisMutationStorageOwner::')):category='storage_charge_or_capacity'
   elif n.startswith(('KisPageMetadataCoordinator::','KisShardSlotIndex<','KisPageRecordArena','KisPageWorkingState::','KisPageStateMachine::')):category='metadata_working'
   elif n.startswith(('KisTiles3PageReplicaProvider::','Tiles3ResidentBinding::','KisCpuResidentAllocationIndex<','KisTileData','KisCompletionRegistry::')):category='provider_payload_lifecycle'
   elif n.startswith(('KisPageReadCoordinator::','KisCpuReadBindingLink::','KisCapturedReadView::','KisCpuResidentReadPin::')):category='read_binding'
   elif n.startswith('KisPageOwnerLedger::'):category='owner_backing_ledger'
   elif n.startswith(('KisPageRetirementQueue::','KisPageRetirementRecord::')) or 'ReclamationExecutor::' in n:category='retirement'
   elif n.startswith(('KisImageEpoch','KisRetainedImageEpoch')) or 'resolvePageRoot(' in n:category='epoch_root_transaction'
   elif n.startswith(('KisPageWriteCoordinator::','KisMutationWriteSet::','KisPageMutationSession::','KisPagePublicationCoordinator::')):category='write_protocol'
  mechanisms[category or 'fixture_or_unclassified']+=1
 assert sum(phases.values())==sum(mechanisms.values())==totals['operation_samples']
 fixture=json.loads((path.parent/'result.json').read_text())
 valid_fixture=fixture['exit_code']==0 and not fixture['timed_out']
 return dict(record=path.parent.name,fixture_valid=valid_fixture,totals=dict(totals),core_labels_all_running=dict(cores),
  core_labels_operation=dict(opcores),exclusive_phase_samples=dict(phases),exclusive_mechanism_samples=dict(mechanisms),
  top_operation_leaves=dict(leaves.most_common(25)),sufficient_for_coarse_localization=valid_fixture and totals['operation_samples']>=100,
  xml_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
records=[analyze(p) for p in sorted(H.glob('profile-k*/time-profile.xml'))];assert len(records)==2
(H/'profile-summary.json').write_text(json.dumps({'records':records,
 'scope':'Running samples; source-line/API context is coarse, inline PCs can be ambiguous. No scaling to CPU microseconds or removable budget. Not formal performance qualification.'},indent=2)+'\n')
for r in records:print(json.dumps(r,indent=2))
