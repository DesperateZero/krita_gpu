"""Analyze all fixed diagnostic pairs; no M6 qualification or tail removal."""
from pathlib import Path
import hashlib,json,math,random,statistics

H=Path(__file__).resolve().parent
plan=json.loads((H/'diagnostic-protocol.json').read_text())
runs=json.loads((H/'diagnostic/runs.json').read_text());assert len(runs)==768
assert json.loads((H/'diagnostic/identity-final.json').read_text())['verified']
out=[]
for arch in plan['architectures']:
    for k in plan['K']:
        for case in plan['cases']:
            for cell in plan['cells']:
                g=[r for r in runs if (r['arch'],r['K'],r['case'],r['cell'])==(arch,k,case,cell)]
                logs=[];typical=[]
                for pair in range(plan['pairs']):
                    d={r['arm']:r for r in g if r['pair']==pair};assert len(d)==2
                    a,b=d[0]['observation'],d[1]['observation']
                    logs.append(math.log(b['throughput']/a['throughput']))
                    typical.append(math.log(a['median_ns']/b['median_ns']))
                units=[(logs[i]+logs[i+1])/2 for i in range(0,len(logs),2)]
                rng=random.Random(261009)
                boot=sorted(statistics.median(rng.choices(units,k=len(units))) for _ in range(20000))
                lower,upper=math.exp(boot[500]),math.exp(boot[19500])
                out.append({'arch':arch,'K':k,'case':case,'cell':cell,'pairs':len(logs),'blocks':len(units),
                 'throughput_ratio':math.exp(statistics.median(units)),'diagnostic_95pct_interval':[lower,upper],
                 'descriptively_inside_2pct':lower>=.98 and upper<=1.02,
                 'paired_log_throughput_sd':statistics.stdev(logs),
                 'paired_log_median_latency_sd':statistics.stdev(typical),
                 'median_latency_ratio':math.exp(statistics.median(typical)),
                 'median_top1pct_fraction':statistics.median(r['observation']['top_1pct_wall_fraction'] for r in g),
                 'maximum_operation_ns':max(r['observation']['maximum_ns'] for r in g),
                 'observed_qos_before':sorted({r['qos']['qos_before'] for r in g}),
                 'observed_qos_after':sorted({r['qos']['qos_after'] for r in g}),
                 'qos_changed_processes':sum(r['qos']['qos_before']!=r['qos']['qos_after'] for r in g),
                 'observed_nice':sorted({r['qos']['nice'] for r in g})})
report={'protocol_sha256':hashlib.sha256((H/'diagnostic-protocol.json').read_bytes()).hexdigest(),
 'analysis_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'processes':len(runs),'rows':out,
 'qualification':'Descriptive fixed D2 diagnosis only; unadjusted95pct intervals, not formal family qualification. No tail removed or normalization',
 'product_modified':False,'previous_qualification_changed':False}
(H/'diagnostic-summary.json').write_text(json.dumps(report,indent=2)+'\n')
for r in out:
 print(r['arch'],r['K'],r['case'],r['cell'],'ratio/CI',round(r['throughput_ratio'],5),
       [round(v,5) for v in r['diagnostic_95pct_interval']],'sd',round(r['paired_log_throughput_sd'],4),
       'qos',r['observed_qos_before'],r['observed_qos_after'])
