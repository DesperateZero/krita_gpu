#!/usr/bin/env python3
"""Frozen blocks, work units and prospective r1 prediction; no sample selection."""
import hashlib,json,random,statistics
from pathlib import Path
H=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['merge','deferred_clear','flushed_clear','fused_clear','failed_fusion','initialized_bytes','pixel_operations','fill_operations','accepted_cold_plans','new_batches','successful_seals','commits']
mechanisms={}
for batch in ['capability','r1-capability']:
    rows=json.loads((H/batch/'results.json').read_text());assert len(rows)==(5 if batch=='capability' else 4) and all(r['passed'] for r in rows)
    summary=[]
    for r in rows:
        for c in r['counts']:
            v=dict(zip(names,c['values']));assert len(c['values'])==12
            assert v['deferred_clear']==v['flushed_clear']+v['fused_clear']
            assert v['successful_seals']<=v['new_batches'] and v['failed_fusion']==0
            if c['stage']==2:assert v['merge']==19 and v['pixel_operations']==19
            summary.append({'index':r['index'],'configuration':r['configuration'],'stage':c['stage'],**v})
    mechanisms[batch]=summary
def bootstrap(values):
    rng=random.Random(20261010);n=len(values)
    samples=sorted(statistics.median(rng.choices(values,k=n)) for _ in range(50000))
    return [samples[int(.025*(len(samples)-1))],samples[int(.975*(len(samples)-1))]]
performance={}
for batch,blocks in [('explore',4),('r1-confirm',16)]:
    rows=json.loads((H/batch/'results.json').read_text());assert len(rows)==blocks*4 and all(r['passed'] for r in rows)
    results=[]
    for stage in ['Setup','Stroke','Undo','Redo','Teardown']:
        for metric in ['cpu_ns','wall_ns']:
            deltas=[];relatives=[];control=[];fusion=[]
            for b in range(blocks):
                block=rows[4*b:4*b+4]
                values={c:statistics.mean(next(s[metric] for s in r['stages'] if s['stage']==stage) for r in block if r['configuration']==c)/1e6 for c in ['control','fusion']}
                assert sum(r['configuration']=='control' for r in block)==2
                deltas.append(values['control']-values['fusion']);relatives.append(100*deltas[-1]/values['control']);control.append(values['control']);fusion.append(values['fusion'])
            point=statistics.median(deltas)
            row=dict(stage=stage,metric=metric,block_savings_ms=deltas,median_block_saving_ms=point,median_block_relative_saving_percent=statistics.median(relatives),median_control_block_mean_ms=statistics.median(control),median_fusion_block_mean_ms=statistics.median(fusion))
            if batch=='r1-confirm':row['pointwise_95_ci_ms']=bootstrap(deltas)
            results.append(row)
    performance[batch]=results
primary=next(r for r in performance['r1-confirm'] if r['stage']=='Stroke' and r['metric']=='cpu_ns')
value=primary['median_block_saving_ms']>=.5 and primary['pointwise_95_ci_ms'][0]>0
result=dict(mechanisms=mechanisms,performance=performance,prototype_value_screen_passed=value,prediction={'engineering_range_ms':[1,2],'point_within_range':1<=primary['median_block_saving_ms']<=2,'not_calibration_proof':'Broad range and no frozen point prediction; no success probability or ranking claim.'},inputs={str(p):sha(p) for p in [H/'PROTOCOL.md',H/'R1_PREDICTION.md',H/'capability/results.json',H/'r1-capability/results.json',H/'explore/results.json',H/'r1-confirm/results.json',Path(__file__)]},limits='Independent r1 prototype endpoint only; stage CIs pointwise, no family or production qualification; not compared to upstream.')
(H/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'primary':primary,'prototype_value_screen_passed':value},indent=2))
