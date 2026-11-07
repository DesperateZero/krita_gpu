"""Reproducible quantity attribution; all timings deliberately excluded."""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import struct
import subprocess

HERE=Path(__file__).resolve().parent
maps={}
images=defaultdict(dict)
for path in sorted(HERE.glob('run-*/events.bin.maps.tsv')):
    m={}
    for line in path.read_text().splitlines():
        address,base,image,name=line.split('\t',3)
        address,base=int(address,16),int(base,16)
        m[address]=(image,address-base,name)
        images[image][address-base]=name
    maps[path.parent.name]=m
symbols={}
symbol_dir=HERE/'symbols'
symbol_dir.mkdir(exist_ok=True)
for image,addresses in sorted(images.items()):
    offsets=sorted(addresses)
    key=hashlib.sha256(image.encode()).hexdigest()[:16]
    output=symbol_dir/(key+'.json')
    if output.exists():
        result=json.loads(output.read_text())
        assert result['offsets']==offsets and result['image']==image
    else:
        if Path(image).exists() and ('krita_gpu' in image):
            inputs=symbol_dir/(key+'.txt')
            inputs.write_text(''.join(hex(v)+'\n' for v in offsets))
            cmd=['atos','-o',image,'-arch','arm64','-offset','-inlineFrames','-d',' || ','-f',str(inputs)]
            proc=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
            assert proc.returncode==0,(image,proc.stderr)
            groups=proc.stdout.split('\n || \n')
            if not groups[-1].strip(): groups.pop()
            lines=[' || '.join(g.splitlines()) for g in groups]
            assert len(lines)==len(offsets),(image,len(lines),len(offsets))
        else:
            cmd=[];lines=[addresses[v] or hex(v) for v in offsets]
        result=dict(image=image,offsets=offsets,symbols=lines,command=cmd)
        output.write_text(json.dumps(result,indent=2)+'\n')
    for offset,symbol in zip(offsets,result['symbols']):symbols[(image,offset)]=symbol

def stack(event,mapping):
    names=[]
    for pc in event[7:]:
        if not pc: continue
        if pc not in mapping: names.append(hex(pc));continue
        image,offset,fallback=mapping[pc]
        names.extend(symbols[(image,offset)].split(' || '))
    return names

SKIP=('br1Trace(', 'KisMutationStorageOwner::', 'kisAllocateMutationStorage(',
      'kisFreeMutationStorage(', 'KisBackingBudgetController::fitsLocked(',
      'std::','boost::', 'intrusive_ptr_', 'KisMutationStorageAllocator<',
      'KisPageWorkingArray<')
def caller(names):
    for name in names:
        if any(name.startswith(s) for s in SKIP):continue
        if 'Kis' in name or 'ReclamationExecutor::' in name:return name
    return next((n for n in names if n.startswith('main ')), 'unresolved')

def role(names):
    for name in names:
        if any(name.startswith(s) for s in SKIP):continue
        if name.startswith(('KisPageWorking','KisPageStateMachine::')):return 'working_values'
        if name.startswith('KisPageMetadataCoordinator::'):
            if 'installCpuReadBinding' in name:return 'read_link'
            if 'applyProjectedSequence' in name:return 'working_projection'
            if 'preparePublication' in name or 'PreparedPublication::' in name:return 'metadata_publication'
            return 'metadata_other'
        if name.startswith(('KisPageRecordArena','KisShardSlotIndex')):return 'metadata_arena'
        if name.startswith(('KisTiles3PageReplicaProvider::','Tiles3ResidentBinding::','KisCpuResidentAllocationIndex<','KisTileData')):return 'provider_native'
        if name.startswith(('KisPageReadCoordinator::','KisCpuReadBindingLink::','KisCapturedReadView::','KisCpuResidentReadPin::')):return 'read_view'
        if name.startswith('KisPageOwnerLedger::'):return 'owner_ledger'
        if name.startswith(('KisImageEpoch','KisRetainedImageEpoch','makePageRoot(','buildBalancedPageRoot(','updatePageRoot','resolvePageRoot(')):return 'epoch_root'
        if name.startswith(('KisPageRetirement','ReclamationExecutor::','KisPageStoreReclamation')):return 'retirement'
        if name.startswith('KisCompletionRegistry::'):return 'completion'
        if name.startswith('KisPagePublicationCoordinator::'):return 'publication_descriptor'
        if name.startswith(('KisPageMutation','KisPageWriteCoordinator::','KisMutationWriteSet::')):return 'write_protocol'
        if name.startswith(('KisBackingBudgetController::','kisMutationStorageOwner(')):return 'budget_owner'
        if name.startswith(('KisTiledDataManager','KisPageStore::')):return 'store_adapter'
    return 'unresolved'

KIND={1:'fits',2:'control_request',3:'control_success',4:'retained_request',5:'retained_free',
      6:'deref',7:'raw_free',8:'local_prepare',9:'parent_prepare',10:'local_settle',11:'parent_settle'}
records=[]
for path in sorted(HERE.glob('run-*/events.bin')):
    result=json.loads((path.parent/'result.json').read_text())
    raw=path.read_bytes();magic,count,main,width=struct.unpack_from('<4Q',raw)
    assert magic==0x4252315452414345 and len(raw)==32+count*width
    events=list(struct.iter_unpack('<23Q',raw[32:]))
    mapping=maps[path.parent.name]
    cache={}
    def info(e):
        key=e[7:]
        if key not in cache:
            names=stack(e,mapping)
            cache[key]=(role(names),caller(names),names)
        return cache[key]
    byphase={}
    for phase in sorted({e[1] for e in events}):
        for who in ['main','worker']:
            selected=[e for e in events if e[1]==phase and (e[0]==main)==(who=='main')]
            if not selected:continue
            counts=Counter(KIND[e[2]] for e in selected)
            roles=defaultdict(Counter);top=defaultdict(Counter);capacities=Counter()
            for e in selected:
                r,c,names=info(e);kind=KIND[e[2]]
                roles[kind][r]+=1;top[kind][c]+=1
                if e[2]==3:capacities[r]+=e[5]
            byphase[f'{phase}-{who}']=dict(counts=dict(counts),roles={k:dict(v) for k,v in roles.items()},
                callers={k:[{'caller':c,'count':n} for c,n in v.most_common()] for k,v in top.items()},
                allocated_capacity=dict(capacities))
    # Match only observed successful controlled allocations. Requests routed to
    # process storage without a controller have no success event here.
    live={};allocations=[];unmatched_frees=0;reuses=[];previous_phase=None
    for i,e in enumerate(events):
        if result['workload']=='public' and previous_phase==1 and e[1]!=1:
            for a in live.values(): a['unobserved_warm_gap']=True
            live.clear()
        previous_phase=e[1]
        if e[2]==3:
            r,c,names=info(e)
            a=dict(index=i,tid=e[0],phase=e[1],owner=e[3],pointer=e[4],capacity=e[5],role=r,caller=c)
            if e[4] in live:
                reuses.append(dict(previous=live[e[4]]['index'],next=i,pointer=e[4]))
                live[e[4]]['ambiguous']=True;a['ambiguous']=True
            live[e[4]]=a;allocations.append(a)
        elif e[2] in (5,7) and e[4]:
            a=live.pop(e[4],None)
            if a is None:unmatched_frees+=1
            else:a.update(free_index=i,free_phase=e[1],free_thread=e[0],free_kind=KIND[e[2]])
    lifetime={}
    for phase in sorted({a['phase'] for a in allocations}):
        buckets=defaultdict(Counter);capacity_buckets=defaultdict(Counter)
        for a in allocations:
            if a['phase']!=phase or a['tid']!=main:continue
            if a.get('ambiguous'):outcome='ambiguous_address_reuse'
            elif a.get('unobserved_warm_gap'):outcome='unobserved_warm_gap'
            elif 'free_phase' not in a:outcome='unclosed_at_capture_end'
            elif a['free_phase']==phase:outcome='freed_same_phase'
            else:outcome='freed_later_phase_'+str(a['free_phase'])
            if a.get('free_thread',main)!=main:outcome+='-worker'
            buckets[a['role']][outcome]+=1
            capacity_buckets[a['role']][outcome]+=a['capacity']
        lifetime[str(phase)]={'counts':{k:dict(v) for k,v in buckets.items()},
                              'capacity':{k:dict(v) for k,v in capacity_buckets.items()}}
    record=dict(run=path.parent.name,block=result['block'],workload=result['workload'],row=result['row'],
                events=count,main_tid=main,phases=byphase,lifetime=lifetime,
                observed_allocations=len(allocations),unmatched_frees=unmatched_frees,
                ambiguous_reuses=reuses,unresolved_stack_count=sum(1 for v in cache.values() if v[0]=='unresolved'))
    (path.parent/'attribution.json').write_text(json.dumps(record,indent=2)+'\n')
    # Preserve all exact allocation/free matches and representative full stacks.
    (path.parent/'allocation-lifetimes.json').write_text(json.dumps(allocations,indent=2)+'\n')
    (path.parent/'stacks.json').write_text(json.dumps([dict(frames=v[2],role=v[0],caller=v[1]) for v in cache.values()],indent=2)+'\n')
    records.append(record)
    op=[1,2] if result['workload']=='public' else [10,11,12,13]
    counts=Counter()
    for phase in op:counts.update(byphase.get(f'{phase}-main',{}).get('counts',{}))
    print(path.parent.name,result['row'],dict(counts),'ambiguous',len(reuses),flush=True)
(HERE/'attribution.json').write_text(json.dumps({'qualification':'Quantity/lifetime evidence only; trace times excluded',
    'rules':{'phase':'All-thread phase is temporal, not ownership','matching':'Observed success pointer to first observed matching free; reuse conflicts retained',
    'caveat':'Tracing off across public warm interval leaves first-write lifetimes incomplete; phase2 captures later operation through close'},
    'records':records},indent=2)+'\n')
