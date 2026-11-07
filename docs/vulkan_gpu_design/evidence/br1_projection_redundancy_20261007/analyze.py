#!/usr/bin/env python3
from collections import Counter,defaultdict
import json,statistics
from pathlib import Path
H=Path(__file__).resolve().parent
records=json.loads((H/'results-v3.json').read_text());reports=[]
for row in records:
    before={d['role']:d for d in row['snapshots'][0]['devices']}
    after={d['role']:d for d in row['snapshots'][1]['devices']}
    delta={role:{k:v-before[role][k] for k,v in d.items() if k.startswith(('work.','mutation.','publication.'))} for role,d in after.items()}
    root=delta['root.original'];node=delta['node.paint']
    assert root['mutation.generationsReserved']==149 and root['work.nativeDuplicatePages']==89
    assert root['mutation.operationSessionsCreated']==32 and node['mutation.generationsReserved']==76
    assert row['samples'][0]['projection_updates']==19
    result=dict(index=row['index'],side=row['side'],stroke_wall_ns=row['samples'][0]['stroke_to_projection_ready_ns'],node=node,root=root)
    if row['events']:
        events=row['events'];begins=[e for e in events if e['event']=='begin'];ends=[e for e in events if e['event']=='end']
        assert len(begins)==len(ends)==21 and all(not e['temp'] for e in begins)
        assert {e['merge'] for e in begins}=={e['merge'] for e in ends}==set(range(1,22))
        # This fixture emits 19 stroke updates plus one undo and one redo merge.
        # Independent cumulative counters validate the generation partition below.
        stroke=[e for e in events if e['merge']<=19]
        undo=[e for e in events if e['merge']==20];redo=[e for e in events if e['merge']==21]
        preparations=[e for e in stroke if e['event']=='prepared']
        assert len(preparations)==root['mutation.generationsReserved']==149
        assert sum(e['event']=='prepared' for e in undo)==0
        assert sum(e['event']=='prepared' for e in redo)==56
        for snapindex,expected in [(2,0),(3,56)]:
            a=next(d for d in row['snapshots'][snapindex-1]['devices'] if d['role']=='root.original')
            b=next(d for d in row['snapshots'][snapindex]['devices'] if d['role']=='root.original')
            assert b['mutation.generationsReserved']-a['mutation.generationsReserved']==expected
        stores={e['store'] for e in preparations};assert len(stores)==1
        # Store and backend are different objects; counters plus one non-null store validate coverage.
        assert all(e['store']!='0' for e in preparations)
        import re
        raw=(H/f"run-v3-{row['index']:02}-{row['side']}"/'fixture.log').read_text()
        used,capacity=map(int,re.findall(r'BR1_PROJECTION_BUFFER (\d+) (\d+)',raw)[0])
        assert used==len(events) and used<capacity
        bypage=defaultdict(list);bymerge=defaultdict(list)
        for e in preparations:
            bypage[(e['merge'],e['store'],tuple(e['page']))].append(e);bymerge[e['merge']].append(e)
        duplicates=[]
        for key,values in bypage.items():
            if len(values)==1:continue
            assert len(values)==2
            first,second=sorted(values,key=lambda e:e['start_wall_ns'])
            assert first['phase']=='clear' and second['phase']=='composite'
            assert second['has_source'] and first['target_generation']==second['source_generation']
            # Observed starts: absence of another writer is not a future scheduling guarantee.
            intervening=[e for e in preparations if e['merge']!=second['merge'] and e['page']==second['page']
                and first['start_wall_ns']<e['start_wall_ns']<second['start_wall_ns']]
            assert not intervening
            duplicates.append(second)
        assert len(duplicates)==53 and len(bypage)==96
        clear_scopes={(e['merge'],e['operation'],e['scope']) for e in preparations if e['phase']=='clear'}
        composite_scopes={(e['merge'],e['operation'],e['scope']) for e in preparations if e['phase']=='composite'}
        assert len(clear_scopes)==13 and len(composite_scopes)==19
        assert len(clear_scopes)+len(composite_scopes)==root['mutation.operationSessionsCreated']
        clear_targets=defaultdict(set);composite_targets=defaultdict(set)
        for e in stroke:
            if e['event']=='targets':
                (clear_targets if e['phase']=='clear' else composite_targets)[e['merge']].add(tuple(e['page']))
        merges=[]
        for merge in range(1,20):
            pages=bymerge[merge];c={tuple(e['page']) for e in pages if e['phase']=='clear'};b={tuple(e['page']) for e in pages if e['phase']=='composite'}
            assert c<=b
            merges.append(dict(merge=merge,clear_prepared=len(c),composite_prepared=len(b),union=len(c|b),duplicate=len(c&b),
                clear_declared=len(clear_targets[merge]),composite_declared=len(composite_targets[merge])))
        result.update(merges=merges,prepared_phases=dict(Counter(e['phase'] for e in preparations)),
            source_phases=dict(Counter(e['phase'] for e in preparations if e['has_source'])),
            duplicate_pages=53,direct_source_chains=53,duplicate_logical_bytes=53*16384,
            union_pages=96,clear_scopes=13,composite_scopes=19,
            duplicate_prepare_cpu_ns=sum(e['cpu_ns'] for e in duplicates),
            duplicate_prepare_wall_ns=sum(e['wall_ns'] for e in duplicates),
            all_prepare_cpu_ns=sum(e['cpu_ns'] for e in preparations),
            operations_cpu_ns=sum(e['cpu_ns'] for e in stroke if e['event']=='operation_end'),
            conditional_generation_after=149-53,conditional_native_duplicates_after=89-53,
            conditional_root_sessions_after=32-13)
    reports.append(result)
traces=[r for r in reports if 'duplicate_pages' in r]
cpu=statistics.mean(r['duplicate_prepare_cpu_ns'] for r in traces)
wall=statistics.mean(r['stroke_wall_ns'] for r in reports if r['side']=='original')
sensitivity=[dict(critical_fraction=f,removed_wall_ns=cpu*f,latency_reduction=cpu*f/wall) for f in [0,.25,.5,1]]
summary=dict(records=reports,prediction_calibration=dict(duplicate_cpu_mean_ns=cpu,original_stroke_wall_mean_ns=wall,
    sensitivity=sensitivity,formula='delta_wall = critical_fraction * deleted_prepare_cpu - added_scope_cost + other_cost_and_wait_change',
    interpretation='Conditional planning model, not measured candidate gain, confidence interval or certified deletion. Counts cover original live root. Generation preparation CPU includes allocation/copy/metadata and two clock queries; it is nested within operation CPU and must not be added to it. Additional removed seal/session costs are not priced; new scope/serialization costs are unknown.'),
    scope='Parent-only diagnosis; implemented subset and actual gain are reported separately in comparison-summary.json',
    formal_m6_new_passes=0)
(H/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'duplicate_pages':53,'duplicate_bytes':53*16384,'conditional_root_generations':'149 -> 96',
    'duplicate_cpu_ms':[r['duplicate_prepare_cpu_ns']/1e6 for r in traces],'sensitivity':sensitivity}))
