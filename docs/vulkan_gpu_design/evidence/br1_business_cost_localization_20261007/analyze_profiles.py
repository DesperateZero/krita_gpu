#!/usr/bin/env python3
from bisect import bisect_right
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

H=Path(__file__).resolve().parent


def xml(path):
    root=ET.parse(path).getroot();ids={e.get('id'):e for e in root.iter() if e.get('id')}
    def resolve(e):return ids[e.get('ref')] if e.get('ref') else e
    return root,resolve


def analyze(folder):
    signposts,resolve=xml(folder/'signposts.xml');pending={};intervals=[];counts=Counter()
    for row in signposts.iter('row'):
        values=[resolve(e) for e in row]
        if values[9].text!='org.krita.br1.cost-probe':continue
        timestamp=int(values[0].text);event=values[3].text;name=values[6].text
        key=(values[2].get('fmt'),values[5].text,name)
        if event=='Begin':
            assert key not in pending,key
            pending[key]=timestamp
        elif event=='End':
            if key not in pending:counts['unmatched_end']+=1;continue
            start=pending.pop(key);assert timestamp>start
            intervals.append((start,timestamp,name));counts[name]+=1
    counts['unmatched_begin']=len(pending)
    intervals.sort();assert all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:]))
    starts=[x[0] for x in intervals]
    root,resolve=xml(folder/'time-profile.xml');totals=Counter();groups=defaultdict(lambda:defaultdict(Counter));raw=[]
    for row in root.iter('row'):
        timestamp,thread,process,core,state,weight,backtrace=[resolve(e) for e in row]
        totals['all_samples']+=1
        if state.text!='Running':totals['not_running_samples']+=1;continue
        t=int(timestamp.text);index=bisect_right(starts,t)-1
        phase=intervals[index][2] if index>=0 and t<intervals[index][1] else 'Outside'
        frames=[resolve(e) for e in backtrace];names=[f.get('name','') for f in frames]
        group=groups[phase];group['counts']['running_samples']+=1
        group['threads'][thread.get('fmt','')]+=1;group['cores'][core.get('fmt','')]+=1
        group['leaf'][names[0] if names else '<empty>']+=1
        for name in set(names):group['inclusive'][name]+=1
        # KisUpdateJobItem dispatches both MERGE and STROKE: never infer actor from it.
        actor=('projection' if any(n.startswith(('KisAsyncMerger::','KisUpdateOriginalVisitor::')) for n in names)
               else 'stroke' if any(n.startswith(('FreehandStrokeStrategy::','KisDabRendering','KisPainterBasedStrokeStrategy::','TestUtil::runMatchedFreehandBaseline()::Strategy::')) for n in names)
               else 'history_collector' if any(n.startswith('KisPageHistoryCollector::') for n in names)
               else 'retirement' if any(n.startswith('KisPageRetirementQueue::') for n in names)
               else 'reclamation_dispatch' if any('ReclamationExecutor::' in n for n in names)
               else 'main' if 'Main Thread' in thread.get('fmt','') else 'other_worker')
        group['actor'][actor]+=1
        category=None
        for frame in frames:
            binary=frame.find('binary')
            if binary is not None and resolve(binary).get('name')=='libsystem_malloc.dylib':category='physical_heap';break
        for name in names:
            if category:break
            if name.startswith(('KisBackingBudget','kisPageStorage','kisAllocatePageStorage','kisFreePageStorage','KisMutationStorageOwner::')):category='budget_storage'
            elif name.startswith(('KisPageMetadata','KisShardSlotIndex','KisPageRecordArena','KisPageWorkingState::','KisPageStateMachine::')):category='metadata'
            elif name.startswith(('KisPageWriteCoordinator::','KisPagePublicationCoordinator::','KisMutationWriteSet::','KisPageMutationSession::','KisPageMutationExecution::')):category='mutation_publication'
            elif name.startswith(('KisImageEpoch','KisRetainedImageEpoch')) or 'resolvePageRoot(' in name:category='epoch'
            elif name.startswith(('KisPageReadCoordinator::','KisCpuReadBindingLink::','KisCapturedReadView::','KisCpuResidentReadPin::','KisPageStoreIteratorReadScope::')):category='read_binding'
            elif name.startswith(('KisTiles3PageReplicaProvider::','Tiles3ResidentBinding::','KisCpuResidentAllocationIndex','KisTileData','KisCompletionRegistry::','KisPageOwnerLedger::')):category='provider_ledger_completion'
            elif name.startswith(('KisPageRetirementQueue::','KisPageRetirementRecord::')) or 'ReclamationExecutor::' in name:category='retirement'
            elif name.startswith(('KisTiledDataManagerPageStore','KisTiledDataManager::')):category='adapter_manager'
            elif name.startswith(('KoComposite','KoOptimizedComposite','KisBrush','KisAutoBrush','KisDabRendering')) or 'compositeVector' in name:category='pixel_brush'
        group['mechanism'][category or 'other']+=1
        if phase in ['Stroke','Undo','Redo','Teardown']:
            raw.append(dict(time=t,phase=phase,thread=thread.get('fmt'),actor=actor,mechanism=category or 'other',frames=names))
    result={'record':folder.name,'complete_intervals':dict(counts),'totals':dict(totals),'phases':{}}
    for phase,group in groups.items():
        result['phases'][phase]={k:dict(v.most_common(100)) for k,v in group.items()}
        result['phases'][phase]['marked_wall_ns']=sum(end-start for start,end,p in intervals if p==phase)
        assert sum(group['mechanism'].values())==group['counts']['running_samples']
    (folder/'selected-stacks.json').write_text(json.dumps(raw,indent=2)+'\n')
    (folder/'intervals.json').write_text(json.dumps(intervals,indent=2)+'\n')
    return result


results=[analyze(p) for p in sorted(H.glob('profile-[0-9]*'))]
assert len(results)==4
(H/'profile-summary.json').write_text(json.dumps({'records':results,'interpretation':'Complete signpost intervals, all-thread Running samples. Exclusive mechanism categories partition samples; inclusive callers overlap. Not microseconds, removable CPU budget, formal timing or confidence intervals.'},indent=2)+'\n')
for r in results:
    print(json.dumps({'record':r['record'],'intervals':r['complete_intervals'],'stages':{
        k:dict(samples=v['counts']['running_samples'],actors=v['actor'],mechanisms=v['mechanism'],top_leaf=dict(list(v['leaf'].items())[:8]))
        for k,v in r['phases'].items() if k in ['Stroke','Undo','Redo','Teardown']}},ensure_ascii=False))
