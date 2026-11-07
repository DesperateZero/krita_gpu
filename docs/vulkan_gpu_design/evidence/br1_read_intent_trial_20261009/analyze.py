#!/usr/bin/env python3
"""Per-block causal screening, not confirmatory confidence intervals."""
import hashlib,json,statistics
from pathlib import Path
H=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
cap=json.loads((H/'capability/results.json').read_text())
rows=json.loads((H/'matrix/results.json').read_text()) if (H/'matrix/results.json').exists() else []
assert all(x['passed'] for x in cap+rows)
result={'input_hashes':{str(H/'capability/results.json'):sha(H/'capability/results.json')},'capability':[],'matrix':{},'ci':None}
for row in cap:
    result['capability'].append({'configuration':row['configuration'],'counts':row['counts'],'stages':row['stages']})
if rows:
    assert len(rows)==16 and ''.join(x['configuration'] for x in rows)=='ABBABAABABBABAAB'
    result['input_hashes'][str(H/'matrix/results.json')]=sha(H/'matrix/results.json')
    for stage in ['Setup','Stroke','Undo','Redo','Teardown','All']:
        for endpoint in ['cpu_ns','wall_ns']:
            def value(row):return sum(s[endpoint] for s in row['stages'] if stage=='All' or s['stage']==stage)/1e6
            blocks=[]
            for b in range(4):
                block=rows[4*b:4*b+4]
                av=statistics.mean(value(x) for x in block if x['configuration']=='A');bv=statistics.mean(value(x) for x in block if x['configuration']=='B')
                blocks.append({'block':b,'A_ms':av,'B_ms':bv,'saving_ms':av-bv})
            savings=[x['saving_ms'] for x in blocks]
            result['matrix'][stage+'_'+endpoint]={'blocks':blocks,'median_block_saving_ms':statistics.median(savings),'mean_block_saving_ms':statistics.mean(savings),'range_ms':[min(savings),max(savings)],'A_values_ms':[value(x) for x in rows if x['configuration']=='A'],'B_values_ms':[value(x) for x in rows if x['configuration']=='B']}
    s=result['matrix']['Stroke_cpu_ns'];result['passes_stroke_exploratory_threshold']=s['range_ms'][0]>0 and s['median_block_saving_ms']>=.3
    result['processes']=len(cap)+len(rows)
    # Runtime libraries other than the selected image must match every process.
    dependencies=[]
    for batch,items in [('capability',cap),('matrix',rows)]:
        for row in items:
            runtime=json.loads((H/batch/f"{row['index']:02}-{row['configuration']}"/'runtime.json').read_text())
            dependencies.append({p:v for p,v in runtime.items() if not p.endswith('/libkritaimage.21.0.0.dylib')})
    assert all(x==dependencies[0] for x in dependencies)
    result['shared_runtime_dependencies']=dependencies[0]
    result['same_dependencies']=True
(H/'summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in result.items() if k in ['processes','passes_stroke_exploratory_threshold','same_dependencies']}))
for k,v in result['matrix'].items(): print(k,v['median_block_saving_ms'],v['range_ms'])
