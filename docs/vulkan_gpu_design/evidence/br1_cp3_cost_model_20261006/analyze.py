"""Derive costs without changing the frozen gate estimators."""
import json
import math
from pathlib import Path
import statistics as st

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent/'br1_cp3_candidate_storage_20261006'
rows = json.loads((HERE/'runs/results.json').read_text())
protocol = json.loads((HERE/'protocol.json').read_text())
assert len(rows) == 144 and all(r['exit_code']==0 and r['reaped'] and r['image_loaded'] for r in rows)
assert json.loads((HERE/'runs/identity-final.json').read_text())['inputs_verified']

def summary(values):
    return dict(median=st.median(values), minimum=min(values), maximum=max(values), samples=len(values))

public = []
profile = []
for case, spec in enumerate(protocol['public_unprofiled_cases']):
    N,K,B,height,mode = spec
    for variant in ['m5','current']:
        data = [r['data'][0] for r in rows if r['kind']=='public' and r['case']==case and r['variant']==variant]
        assert len(data)==4
        for d in data:
            for period, operations in [('first_counts',1),('steady_counts',d['completed'])]:
                c=d[period]
                expected = dict(duplicate_pages=K if mode=='public' and height==1 else 0,
                                duplicate_bytes=K*64*64*B if mode=='public' and height==1 else 0,
                                payload_pages=K if mode=='public' and height==64 else 0,
                                payload_bytes=K*64*64*B if mode=='public' and height==64 else 0,
                                generations=K if mode=='public' else 0,
                                sealed_pages=K if mode=='public' else 0,
                                sessions=1 if mode=='public' else 0,
                                commits=1 if mode=='public' else 0, default_bytes=0, preclone_hits=0)
                assert all(c[f]==count*operations for f,count in expected.items()), (d,period)
                assert c['foreground_copy_bytes']==c['duplicate_bytes']
        public.append(dict(case=case,variant=variant,N=N,K=K,B=B,height=height,mode=mode,
                           wall_us=summary([d['wall_ns']/d['completed']/1000 for d in data]),
                           thread_cpu_us=summary([d['thread_cpu_ns']/d['completed']/1000 for d in data]),
                           process_cpu_us=summary([d['process_cpu_ns']/d['completed']/1000 for d in data]),
                           counts_per_operation={f:v/data[0]['completed'] for f,v in data[0]['steady_counts'].items()}))
for case in [0,1]:
    for variant in ['m5','current']:
        data=[r['data'][0] for r in rows if r['kind']=='profile' and r['case']==case and r['variant']==variant]
        for d in data:
            for name, operations in [('first_counts',1),('steady_counts',d['completed'])]:
                c=d[name]
                assert c['duplicate_pages']==d['K']*operations
                assert c['duplicate_bytes']==d['K']*4096*d['B']*operations
                assert c['foreground_copy_bytes']==c['duplicate_bytes'] and c['preclone_hits']==0
                assert c['generations']==c['sealed_pages']==d['K']*operations
                assert c['sessions']==c['commits']==operations
                assert c['payload_pages']==c['payload_bytes']==c['default_bytes']==0
        names=sorted({p['phase'] for d in data for p in d['phases']})
        profile.append(dict(case=case,variant=variant,
                            profiled_wall_us=summary([d['wall_ns']/d['completed']/1000 for d in data]),
                            phases={name:dict(wall_us=summary([next((p['wall_ns']/d['completed']/1000 for p in d['phases'] if p['phase']==name),0) for d in data]),
                                              cpu_us=summary([next((p['cpu_ns']/d['completed']/1000 for p in d['phases'] if p['phase']==name),0) for d in data])) for name in names},
                            limits='Nested inclusive, opt-in clocks; current/M5 phase densities differ. Localization only, no additive or causal subtraction.'))
native=[]
phase_fields=['begin_ns','acquire_ns','payload_ns','page_other_ns','seal_ns','root_commit_ns']
for arch in protocol['native_arch']:
    for K in [1,16]:
        for variant in ['fresh','handoff']:
            groups={cuts:[r for r in rows if r['kind']=='native' and r['arch']==arch and r['K']==K
                         and r['native_variant']==variant and r['cuts']==cuts] for cuts in [False,True]}
            off=[d for r in groups[False] for d in r['data']]
            on=[d for r in groups[True] for d in r['data']]
            for d in off+on:
                assert d['before_copy_bytes']==(K*16384 if variant=='fresh' else 0)
                assert d['foreground_copy_bytes']==d['before_copy_bytes'] and d['preclone_hits']==0
                if d['cuts']: assert sum(d[f] for f in phase_fields)==d['commit_ns']
            native.append(dict(arch=arch,K=K,variant=variant,
                               unprofiled_total_us=summary([d['commit_ns']/1000 for d in off]),
                               cuts_total_us=summary([d['commit_ns']/1000 for d in on]),
                               median_total_shift_percent=(st.median([d['commit_ns'] for d in on])/st.median([d['commit_ns'] for d in off])-1)*100,
                               phases_us={f:summary([d[f]/1000 for d in on]) for f in phase_fields},
                               acquire_plus_seal_commit_share=summary([(d['acquire_ns']+d['seal_ns']+d['root_commit_ns'])/d['commit_ns'] for d in on]),
                               seal_commit_share=summary([(d['seal_ns']+d['root_commit_ns'])/d['commit_ns'] for d in on]),
                               before_copy_bytes_per_operation=off[0]['before_copy_bytes'],
                               limits='Exclusive cuts close arithmetically on each instrumented sample. Medians are not additive; ranges include all cold samples. Instrumentation/ordering shifts forbid formal reuse.'))

fixed = json.loads((PREVIOUS/'fixed-m5-fresh-summary.json').read_text())
formal_latency = json.loads((PREVIOUS/'latency-summary.json').read_text())
budgets=[]
for d in formal_latency['observations']:
    cap=d['fresh_median_ns']*(1-d['required_reduction'])
    gap=d['handoff_median_ns']-cap
    delta=d['fresh_median_ns']-d['handoff_median_ns']
    budgets.append(dict(arch=d['arch'],K=d['K'],fresh_us=d['fresh_median_ns']/1000,
                        handoff_us=d['handoff_median_ns']/1000,
                        cap_us_if_fresh_held_fixed=cap/1000,
                        gap_us_if_fresh_held_fixed=gap/1000,
                        handoff_reduction_needed_if_fresh_fixed=gap/d['handoff_median_ns'],
                        shared_work_removal_us_if_delta_held_fixed=(d['fresh_median_ns']-delta/d['required_reduction'])/1000,
                        limits='Descriptive separate medians, not the formal paired estimator or confidence pass. Fresh must not be held fixed when a common-path optimization changes both variants.'))
paired = json.loads((PREVIOUS/'fixed-m5-fresh/runs.json').read_text())
fresh_budgets=[]
for d in fixed['observations']:
    run={(r['pair'],r['variant']):r['data'][0] for r in paired if r['arch']==d['arch'] and r['K']==d['K']}
    block_gaps=[]
    for block in range(20):
        t={v:math.sqrt(math.prod(run[(p,v)]['wall_ns']/run[(p,v)]['completed_operations']
                                 for p in [block*2,block*2+1])) for v in ['m5','current']}
        block_gaps.append((t['current']-t['m5']/.98)/1000)
    fresh_budgets.append(dict(arch=d['arch'],K=d['K'],formal_ratio=d['current_over_m5_throughput'],
                              lower=d['one_sided_9875_lower'],
                              descriptive_paired_block_gap_us=summary(block_gaps),
                              relative_current_time_reduction_from_ratio_point=max(0,1-d['current_over_m5_throughput']/.98),
                              limits='Paired block absolute gaps describe the engineering budget, not a substituted pass statistic. Confidence margin remains required.'))

result=dict(product=protocol['product'],m5=protocol['m5'],qualification='Diagnostic only; all existing failed gates remain failed',
            processes=len(rows),samples=sum(len(r['data']) for r in rows),inputs_verified=True,
            predicted_counts_match_all_first_and_steady_public_intervals=True,
            public=public,profile=profile,native=native,frozen_handoff_budgets=budgets,
            frozen_fresh_budgets=fresh_budgets,
            unresolved=['No calibrated complete cycle/time model or pure management self attribution',
                        'No direct DRAM/cache traffic measurement or per-provider exclusive allocation/copy/accounting split',
                        'No common metadata resident denominator, completed drain, upstream/real stroke/tail qualification',
                        'No demonstrated safety-preserving candidate that closes remaining gaps or proof of unattainability'])
(HERE/'cost-model.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(counts_match=True, processes=len(rows), samples=result['samples'],
                      fresh_budgets=fresh_budgets,handoff_budgets=budgets),indent=2))
