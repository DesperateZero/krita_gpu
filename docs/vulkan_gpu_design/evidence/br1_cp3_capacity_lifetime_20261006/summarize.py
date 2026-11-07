"""Check independent invariants and emit the finite candidate evidence table."""
from collections import Counter
import json
from pathlib import Path
import struct

HERE=Path(__file__).resolve().parent
source=json.loads((HERE/'attribution.json').read_text())
processes=json.loads((HERE/'results.json').read_text())
assert len(processes)==28 and len(source['records'])==14
assert all(r['exit_code']==0 and r['reaped'] and not r['timed_out'] and r['image_loaded'] and r['checks_passed'] for r in processes)
rows=[]
for r in source['records']:
    phases=[2] if r['workload']=='public' else [10,11,12,13]
    counts=Counter();deref=Counter();allocation=Counter();unclassified=Counter()
    for phase in phases:
        v=r['phases'][f'{phase}-main']
        counts.update(v['counts'])
        deref.update(v['roles'].get('deref',{}))
        allocation.update(v['roles'].get('control_success',{}))
        for kind, rs in v['roles'].items(): unclassified[kind]+=rs.get('unresolved',0)
        for kind in ['control_request','control_success','deref']:
            assert not v['roles'].get(kind,{}).get('unresolved',0),r['run']
    assert len({counts[k] for k in ['control_success','local_prepare','parent_prepare','local_settle','parent_settle']})==1
    assert counts['control_request']>=counts['control_success']
    assert not r['ambiguous_reuses']
    raw=(HERE/r['run']/'events.bin').read_bytes()
    events=struct.iter_unpack('<23Q',raw[32:])
    process_routes=sum(e[0]==r['main_tid'] and e[1] in phases and e[2]==2 and e[3]==0 for e in events)
    assert counts['control_request']-counts['control_success']==process_routes
    rows.append(dict(run=r['run'],block=r['block'],workload=r['workload'],row=r['row'],
                     measured_main_counts=dict(counts),deref_roles=dict(deref),
                     controlled_allocation_roles=dict(allocation),process_storage_routes=process_routes,
                     unclassified_main_events=dict(unclassified)))
public=[r for r in rows if r['workload']=='public' and r['row']==[1024,16,4,1]]
assert len(public)==2 and public[0]['measured_main_counts']==public[1]['measured_main_counts']
assert public[0]['deref_roles']==public[1]['deref_roles']
d=public[0]['deref_roles']
working=sum(d[k] for k in ['working_values','working_projection','metadata_publication'])
native={v:[r for r in rows if r['workload']=='native' and r['row']==[v,16]] for v in ['fresh','handoff']}
for rr in native.values(): assert len(rr)==2 and rr[0]['measured_main_counts']==rr[1]['measured_main_counts']
f=native['fresh'][0]['measured_main_counts'];h=native['handoff'][0]['measured_main_counts']
original={r['run']:r for r in source['records']}
common={}
for variant,rr in native.items():
    observed=[]
    for row in rr:
        phases=original[row['run']]['phases']
        observed.append({kind:sum(phases[f'{ph}-main']['counts'][kind] for ph in [12,13])
                         for kind in ['deref','fits']})
    assert observed[0]==observed[1]
    common[variant]=observed[0]
assert common['fresh']['deref']==common['handoff']['deref']
lifetimes=[]
for row in public:
    totals=Counter()
    for values in original[row['run']]['lifetime']['2']['counts'].values():totals.update(values)
    within=sum(n for key,n in totals.items() if key.startswith('freed_same_phase'))
    later=sum(n for key,n in totals.items() if key.startswith('freed_later_phase'))
    unclosed=totals.get('unclosed_at_capture_end',0)
    assert within+later+unclosed==row['measured_main_counts']['control_success']
    lifetimes.append((within,later,unclosed))
assert lifetimes[0]==lifetimes[1]
summary=dict(qualification='Finite quantity/lifetime evidence; no measured optimization speedup or new performance gate',
    processes=28,trace_processes=14,events=sum(r['events'] for r in source['records']),
    all_exit_library_work_identity_checks=True,measured_main_symbolic_coverage='All control requests/successes and deref assigned; other unclassified events explicitly retained per row',
    prepare_settle_success_equality=True,ambiguous_address_reuses=0,
    public_k16_working_chain_deref=dict(count=working,total=sum(d.values()),fraction=working/sum(d.values())),
    native_k16_reductions={k:dict(fresh=f[k],handoff=h[k],reduction_fraction=1-h[k]/f[k])
                          for k in ['control_request','fits','deref','local_prepare']},
    native_common_seal_commit=dict(deref_each=common['fresh']['deref'],fresh_fits=common['fresh']['fits'],handoff_fits=common['handoff']['fits'],
                                  handoff_deref_fraction=common['handoff']['deref']/h['deref'],handoff_fits_fraction=common['handoff']['fits']/h['fits']),
    public_k16_observed_controlled_lifetimes=dict(successes=public[0]['measured_main_counts']['control_success'],free_within_operation=lifetimes[0][0],
        free_later_validation_or_destruction=lifetimes[0][1],unclosed_at_capture_end=lifetimes[0][2],
        limitation='Only controller-backed success events; process storage excluded. Last 45 not a leak verdict or a full-drain measurement.'),
    rows=rows)
(HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2))
