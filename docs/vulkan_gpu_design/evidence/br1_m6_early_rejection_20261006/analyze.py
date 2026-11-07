"""Analyze the fixed new samples without exclusions, extensions or corrections."""
from pathlib import Path
import hashlib
import json
import math
import random
import statistics

H=Path(__file__).resolve().parent
p=json.loads((H/'protocol.json').read_text())
median=statistics.median
result={'parent':p['parent'],'analysis_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'families':{}}
for name in ['parent_comparison','calibration','hit','miss']:
    plan=p[name]; rows=json.loads((H/name/'runs.json').read_text())
    assert len(rows)==plan['buckets']*plan['pairs']*2
    assert json.loads((H/name/'identity-final.json').read_text())['inputs_verified']
    values=[]
    for arch in p['architectures']:
        for k in p['K']:
            for case in (['hit'] if name=='hit' else plan.get('cases',p['cases'])):
                group=[r for r in rows if (r['arch'],r['K'],r['case'])==(arch,k,case)]
                logs=[]; absolute=[]; base=[]; candidate=[]
                for pair in range(plan['pairs']):
                    records={r['image'] if name in ['parent_comparison','calibration'] else r['variant']:r for r in group if r['pair']==pair}
                    keys=('parent','current') if name=='parent_comparison' else ('current','selection') if name=='calibration' else ('off','on')
                    b,t=(records[x] for x in keys)
                    assert all(r['exit_code']==0 and r['reaped'] and r['loaded'] and not r['failures'] and not r['timed_out'] for r in [b,t])
                    assert b['completed']==t['completed']==plan['measured']
                    logs.append(math.log(b['median_ns']/t['median_ns']) if name=='hit' else math.log(t['throughput']/b['throughput']))
                    absolute.append((b['median_ns']-t['median_ns'])/1000)
                    base.append(b['median_ns']/1000);candidate.append(t['median_ns']/1000)
                units=logs if name=='hit' else [(logs[i]+logs[i+1])/2 for i in range(0,len(logs),2)]
                rng=random.Random(plan['seed'])
                boot=sorted(median(rng.choices(units,k=len(units))) for _ in range(plan['bootstrap']))
                alpha=(1-plan['two_sided_confidence'])/2 if 'two_sided_confidence' in plan else 1-plan['one_sided_confidence']
                transform=(lambda x:1-math.exp(-x)) if name=='hit' else math.exp
                point=transform(median(units)); lower=transform(boot[int(alpha*len(boot))]); upper=transform(boot[min(len(boot)-1,int((1-alpha)*len(boot)))])
                passed=lower>0 if name=='hit' else lower>=.98 and upper<=1.02 if name=='calibration' else lower>=.98 if name=='miss' else lower>1
                values.append(dict(arch=arch,K=k,case=case,pairs=plan['pairs'],statistical_units=len(units),point=point,lower=lower,upper=upper,passes=passed,
                    baseline_marginal_median_us=median(base),candidate_marginal_median_us=median(candidate),paired_median_saving_us=median(absolute),
                    metric='latency_reduction' if name=='hit' else 'completed_operation_throughput_ratio'))
    result['families'][name]={'processes':len(rows),'passed':all(v['passes'] for v in values),'rows':values}
for name in ['fixed-m5-fresh','fixed-m5-history']:
    result['families'][name]=json.loads((H/(name+'-summary.json')).read_text())
mechanism=json.loads((H/'mechanism/runs.json').read_text())
mechanism_result=[]
for arch in p['architectures']:
    for k in p['K']:
        for case in p['cases']:
            g={r['image']:r for r in mechanism if (r['arch'],r['K'],r['case'])==(arch,k,case)}
            expected={'hit':[k,k,k,k,k],'single':[0,0,0,0,0],'native-pin':[k,0,0,0,k],'generic-lease':[0,0,0,0,0],'last-use':[0,0,0,0,0]}[case]
            assert g['current']['phase_counts']==[expected],(arch,k,case,g['current']['phase_counts'])
            mechanism_result.append(dict(arch=arch,K=k,case=case,parent=g['parent']['phase_counts'],current=g['current']['phase_counts'],predicted_current=expected,prediction_met=True))
result['mechanism']={'phase_order':['Prepare','Prepared','InstallAttempt','Installed','Cleanup'],'rows':mechanism_result,'timings_excluded':True}
result['qualification']={'mechanism_prediction_met':True,'same_image_hit':result['families']['hit']['passed'],
    'same_image_miss':result['families']['miss']['passed'],'selection_equivalence':result['families']['calibration']['passed'],
    'protected_fresh':result['families']['fixed-m5-fresh']['scoped_family_pass'],'protected_history':result['families']['fixed-m5-history']['scoped_family_pass'],
    'M6_complete':False,'remaining':['Metadata >=25% comparable pre-reconstruction residency denominator','CP0 full required and applicable build qualification','Business natural positive trace/distribution, GPU, M7/M8 remain separate']}
(H/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
for name in ['parent_comparison','calibration','hit','miss']:
    f=result['families'][name];print(name,sum(r['passes'] for r in f['rows']),'/',len(f['rows']))
    for r in f['rows']:print(r['arch'],r['K'],r['case'],round(r['point'],5),round(r['lower'],5),round(r['upper'],5),r['passes'])
