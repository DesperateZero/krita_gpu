#!/usr/bin/env python3
import json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent
load=lambda f:json.loads((H/f).read_text())
mechanism=load('mechanism-results.json');assert len(mechanism)==4 and all(r['passed'] for r in mechanism)
counts=[]
for r in mechanism:
    a={d['role']:d for d in r['snapshots'][0]['devices']};b={d['role']:d for d in r['snapshots'][1]['devices']}
    delta={role:{k:v-a[role][k] for k,v in b[role].items() if k.startswith(('work.','mutation.','publication.'))}
        for role in ['root.original','node.paint']}
    root=delta['root.original'];node=delta['node.paint'];candidate=r['side']=='candidate'
    expected=(132,72,228) if candidate else (149,89,245)
    assert tuple(root[k] for k in ['mutation.generationsReserved','work.nativeDuplicatePages','mutation.writablePinsAcquired'])==expected
    assert root['work.defaultInitializedPages']==60 and root['mutation.operationSessionsCreated']==32
    assert node['mutation.generationsReserved']==76 and node['work.nativeDuplicatePages']==20
    assert node['work.defaultInitializedPages']==56 and node['mutation.writablePinsAcquired']==2420
    assert r['sample']['projection_updates']==19
    counts.append(dict(index=r['index'],side=r['side'],delta=delta))
prices=[];phase_prices=[]
for r in load('results-v3.json'):
    if not r['events']:continue
    bypage=defaultdict(list)
    for e in r['events']:
        if e['event']=='prepared' and e['merge']<=19:bypage[(e['merge'],tuple(e['page']))].append(e)
    sparse=[v for v in bypage.values() if len(v)==2 and any(e['phase']=='clear' and not e['has_source'] for e in v)]
    assert len(sparse)==17
    prices.append(sum(e['cpu_ns'] for v in sparse for e in v))
    phase_prices.append({phase:sum(e['cpu_ns'] for v in sparse for e in v if e['phase']==phase)
        for phase in ['clear','composite']})
rows=load('performance-results.json');assert len(rows)==100 and all(r['passed'] for r in rows)
endpoints=['stroke_to_projection_ready_ns','pen_up_to_projection_ready_ns','undo_drain_ns','redo_drain_ns','owner_teardown_ns','setup_ns','total_fixture_ns']
timing=[]
for arch in ['arm64','x86_64']:
    runs=[r for r in rows if r['arch']==arch and r['phase']=='paired'];assert len(runs)==48
    pairs=defaultdict(dict)
    for r in runs:pairs[r['pair']][r['side']]=r['sample']
    assert set(pairs)==set(range(24)) and all(set(p)=={'parent','candidate'} for p in pairs.values())
    for endpoint in endpoints:
        logs=[math.log(pairs[i]['candidate'][endpoint]/pairs[i]['parent'][endpoint]) for i in range(24)]
        blocks=[statistics.mean(logs[i:i+2]) for i in range(0,24,2)]
        rng=random.Random(261018)
        boot=sorted(math.exp(sum(rng.choice(blocks) for _ in blocks)/len(blocks)) for _ in range(20000))
        def quantile(q):
            x=q*(len(boot)-1);i=int(x);return boot[i]+(boot[min(i+1,len(boot)-1)]-boot[i])*(x-i)
        ratio=math.exp(statistics.mean(blocks));lo,hi=quantile(.025),quantile(.975)
        timing.append(dict(arch=arch,endpoint=endpoint,pairs=24,independent_blocks=12,ratio=ratio,ratio_ci95=[lo,hi],
            latency_reduction=1-ratio,latency_reduction_ci95=[1-hi,1-lo],
            parent_median_ns=statistics.median(p['parent'][endpoint] for p in pairs.values()),
            candidate_median_ns=statistics.median(p['candidate'][endpoint] for p in pairs.values()),
            block_log_ratios=blocks,verdict='positive' if hi<1 else 'regression' if lo>1 else 'inconclusive'))
parent_wall=load('summary.json')['prediction_calibration']['original_stroke_wall_mean_ns']
net_price=statistics.mean(p['composite'] for p in phase_prices)
summary=dict(mechanism=counts,deletion=dict(root_generations=[149,132],root_duplicates=[89,72],root_pins=[245,228],
    total_generations=[225,208],total_duplicates=[109,92],deleted_logical_copy_bytes=278528,
    source_default_initializations_unchanged=116,root_sessions_unchanged=32,
    full_scope_conditional_chains=53,remaining_unproved_chains=36),
    forecast=dict(original_frozen_gross_cpu_ns=prices,original_gross_mean_ns=statistics.mean(prices),
        original_gross_conditional_wall_reduction=[statistics.mean(prices)*f/parent_wall for f in [.25,.5,1]],
        correction='Original forecast overprices net deletion: 17 necessary default initializations move from clear to composite; all116 remain. Gross clear+composite preparation is not deleted CPU. Keep the original plan and label this post-result model correction.',
        parent_phase_cpu_ns=phase_prices,net_duplicate_prepare_price_ns=net_price,
        corrected_conditional_wall_reduction=[net_price*f/parent_wall for f in [.25,.5,1]],
        formula='Before: clear allocate+default-init, composite allocate+copy. After: composite allocate+default-init. If equal required-init cost, net preparation saving approximates one old composite allocate+copy, less added resolves, plus seal/retirement/wait changes.',
        meaning='Post-result conditional price model; unmeasured replacement cost equality and critical-path fraction, no CI or guarantee; instrumented clocks included'),
    timing=timing,work_counts={arch:{side:dict(Counter(r['sample']['projection_updates'] for r in rows if r['arch']==arch and r['side']==side and r['phase']=='paired'))
        for side in ['parent','candidate']} for arch in ['arm64','x86_64']},
    statistics='12 order-balanced blocks, arithmetic mean log ratio, 20,000 block bootstrap seed261018; pointwise diagnostic two-sided95%, no family qualification',
    formal_m6_new_passes=0)
(H/'comparison-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for r in timing:print(r['arch'],r['endpoint'],r['ratio'],r['ratio_ci95'],r['verdict'])
