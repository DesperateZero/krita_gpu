"""Analyze the fixed diagnostic matrix; all estimates remain scoped."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,math,random,statistics
HERE=Path(__file__).resolve().parent
median=statistics.median
runs=json.loads((HERE/'matrix/runs.json').read_text())
assert len(runs)==534 and json.loads((HERE/'matrix/identity-final.json').read_text())['inputs_verified']
groups=defaultdict(dict)
for r in runs:
    assert r['exit_code']==0 and r['loaded'] and r['reaped'] and not r['timed_out'] and not r['failures']
    samples=[json.loads(l) for l in (HERE/'matrix'/r['log']).read_text().splitlines() if l.startswith('{')][8:]
    assert len(samples)==32
    values={}
    for name in ['setup_ns','initialization_ns','close_validation_ns','drain_ns','complete_ns']:
        values[name]=median(s[name] for s in samples)
    for name in ['wall','cpu']:
        values[name]=median(sum(o[name] for o in s['operations']) for s in samples)
        for op in range(r['case'][3]):values[f'{name}_r{op}']=median(s['operations'][op][name] for s in samples)
    values['hits']=[sorted(set(s['operations'][i]['handoffs'] for s in samples)) for i in range(r['case'][3])]
    values['physical_initial']=median(s['operations'][0]['physical_before'] for s in samples)
    values['physical_final']=median(s['operations'][-1]['physical_after'] for s in samples)
    for s in samples:
        for o in s['operations']:
            if r['mode']:
                assert sum(p[0] for p in o['phases'])==o['wall']
                assert sum(p[1] for p in o['phases'])==o['cpu']
                assert sum(m[1] for m in o['metrics'])<=o['wall']
                if r['mode']==2:assert sum(m[2] for m in o['metrics'])<=o['cpu']
    for i in range(6):
        for col,name in enumerate(['wall','cpu']):values[f'phase{i}_{name}']=median(sum(o['phases'][i][col] for o in s['operations']) for s in samples)
    for i in range(20):
        for col,name in enumerate(['calls','wall','cpu','inclusiveWall','inclusiveCpu']):values[f'metric{i}_{name}']=median(sum(o['metrics'][i][col] for o in s['operations']) for s in samples)
    groups[(r['group'],r['arch'],tuple(r['case']),r['variant'],r['mode'],r['image'])][r['block']]=values

def interval(xs):
    rng=random.Random(261006)
    boot=sorted(median(rng.choices(xs,k=len(xs))) for _ in range(20000))
    return [boot[int(.025*len(boot))],boot[int(.975*len(boot))]]
def compare(a,b,field):
    assert a.keys()==b.keys()
    logs=[math.log(a[i][field]/b[i][field]) for i in sorted(a)]
    savings=[a[i][field]-b[i][field] for i in sorted(a)]
    ci=interval(logs);sci=interval(savings)
    return dict(pairs=len(logs),baseline_median_us=median(v[field] for v in a.values())/1000,
                candidate_median_us=median(v[field] for v in b.values())/1000,
                reduction=1-math.exp(-median(logs)),reduction_ci95=[1-math.exp(-ci[0]),1-math.exp(-ci[1])],
                saving_us=median(savings)/1000,saving_ci95_us=[x/1000 for x in sci])

summary={'source':'f0c40a5d195f1c20a0f915faaef18b1f3ee5b575','processes':len(runs),'qualification':'Descriptive diagnostic; no original gate is replaced','timing':[],'calibration':[],'cuts':[],'perturbation':[]}
cases=json.loads((HERE/'protocol.json').read_text())['timing_matrix']['cases']
for arch in ['arm64','x86_64']:
    for case in cases:
        data={v:groups[('timing',arch,tuple(case),v,0,'diagnostic')] for v in ['fresh','handoff','matched']}
        row={'arch':arch,'case':case,'comparisons':{},'conditions':{}}
        for base,candidate in [('fresh','handoff'),('matched','handoff'),('fresh','matched')]:
            row['comparisons'][base+'_to_'+candidate]={field:compare(data[base],data[candidate],field) for field in ['wall','complete_ns','setup_ns','close_validation_ns','drain_ns']+(['cpu'] if arch=='arm64' else [])}
        for v,d in data.items():
            row['conditions'][v]={'hits_by_round':next(iter(d.values()))['hits'],'physical_initial':median(x['physical_initial'] for x in d.values()),'physical_final':median(x['physical_final'] for x in d.values()),'wall_us_by_round':[median(x[f'wall_r{i}'] for x in d.values())/1000 for i in range(case[3])]}
        summary['timing'].append(row)
    for variant in ['fresh','handoff']:
        d={i:groups[('calibration',arch,(16,4,'preserve',1),variant,0,i)] for i in ['production','diagnostic']}
        summary['calibration'].append(dict(arch=arch,variant=variant,wall=compare(d['production'],d['diagnostic'],'wall')))
names=['plan_residual','handoff_physical_prepare','handoff_accounting_prepare','handoff_metadata_prepare','handoff_descriptor_prepare','handoff_joint_install','handoff_cleanup','fresh_provider_wrapper','private_write_prepare','private_publish','provider_allocate_residual','tile_duplicate_including_storage','payload_initialize_including_storage']
for variant in ['fresh','handoff','matched']:
    data={mode:groups[('cuts','arm64',(16,4,'preserve',1),variant,mode,'diagnostic')] for mode in [0,1,2]}
    for mode in [1,2]:
        d=data[mode];row={'variant':variant,'mode':mode,'wall_us':median(x['wall'] for x in d.values())/1000,'cpu_us':median(x['cpu'] for x in d.values())/1000,'phases':[],'metrics':[]}
        for i,n in enumerate(['begin','write_acquire_or_full_input','guard_pixel_write','loop_guard_release_other','seal','commit']):
            row['phases'].append(dict(name=n,wall_us=median(x[f'phase{i}_wall'] for x in d.values())/1000,cpu_us=median(x[f'phase{i}_cpu'] for x in d.values())/1000))
        for i,n in enumerate(names):
            row['metrics'].append(dict(name=n,calls=median(x[f'metric{i}_calls'] for x in d.values()),exclusive_wall_us=median(x[f'metric{i}_wall'] for x in d.values())/1000,exclusive_cpu_us=median(x[f'metric{i}_cpu'] for x in d.values())/1000,inclusive_wall_us=median(x[f'metric{i}_inclusiveWall'] for x in d.values())/1000,inclusive_cpu_us=median(x[f'metric{i}_inclusiveCpu'] for x in d.values())/1000))
        summary['cuts'].append(row)
        summary['perturbation'].append(dict(variant=variant,mode=mode,wall=compare(data[0],d,'wall'),cpu=compare(data[0],d,'cpu')))
summary['clock_calibration']=[];summary['capacity']=[]
for r in json.loads((HERE/'smoke/runs.json').read_text()):
    if r['group'] not in ['clock','capacity']:continue
    samples=[json.loads(l) for l in (HERE/'smoke'/r['log']).read_text().splitlines() if l.startswith('{')]
    if r['group']=='clock':summary['clock_calibration'].append(dict(arch=r['arch'],**samples[0],coverage=samples[0]['clock_cpu']/samples[0]['clock_wall']))
    else:summary['capacity'].append(dict(arch=r['arch'],variant=r['variant'],refused=[s['refused'] for s in samples],before=[s['operations'][0]['physical_before'] for s in samples],after=[s['operations'][0]['physical_after'] for s in samples]))
summary['limits']=['No calibrated immutable lower bound or proof across all legal algorithms.','Instrumented time includes observer overhead; mode comparison is reported, not subtracted as an exact correction.','CPU wall difference is not mutex wait. Rosetta CPU coverage fails calibration and is not interpreted.','Retention in four-operation case includes all four exact pre-operation views; not a freehand product trace.','Complete sample includes synthetic setup, exhaustive validation, close and reclamation barrier, not canvas visible or saturated throughput.','Same-state Fresh diagnostic may retain unnecessary alternate; a legal alternate eviction policy is not benchmarked.','Twelve block intervals are descriptive per comparison, without family qualification.']
summary['analysis_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for r in summary['timing']:
    print(r['arch'],r['case'],{k:{'r':round(v['wall']['reduction']*100,2),'ci':[round(x*100,2) for x in v['wall']['reduction_ci95']],'saved_us':round(v['wall']['saving_us'],2),'whole_r':round(v['complete_ns']['reduction']*100,2)} for k,v in r['comparisons'].items()})
print('calibration',summary['calibration'])
for r in summary['cuts']:
    if r['mode']==1:print('cuts',r['variant'],r['wall_us'],r['cpu_us'],r['phases'],r['metrics'])
print('perturbation',summary['perturbation'])
