#!/usr/bin/env python3
import hashlib,json,random,statistics
from pathlib import Path
H=Path(__file__).resolve().parent
rows=json.loads((H/'matrix/results.json').read_text());cap=json.loads((H/'capability/results.json').read_text())
assert len(rows)==32 and ''.join(x['configuration'] for x in rows)=='ABBABAAB'*4 and all(x['passed'] for x in rows+cap)
result={'input_hashes':{},'mechanism':cap,'endpoints':{},'interval_scope':'exploratory pointwise 95%, block bootstrap, not independent confirmation'}
for p in [H/'matrix/results.json',H/'capability/results.json',H/'PROTOCOL.md',Path(__file__)]:result['input_hashes'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
for stage in ['Setup','Stroke','Undo','Redo','Teardown']:
    for endpoint in ['cpu_ns','wall_ns']:
        def value(row):return next(s[endpoint] for s in row['stages'] if s['stage']==stage)/1e6
        blocks=[]
        for b in range(8):
            group=rows[4*b:4*b+4];a=statistics.mean(value(x) for x in group if x['configuration']=='A');c=statistics.mean(value(x) for x in group if x['configuration']=='B')
            blocks.append({'block':b,'A_ms':a,'B_ms':c,'saving_ms':a-c})
        savings=[b['saving_ms'] for b in blocks];rng=random.Random(20261009)
        boot=sorted(statistics.median(rng.choices(savings,k=8)) for _ in range(10000))
        def q(p):
            i=(len(boot)-1)*p;n=int(i);return boot[n]+(boot[min(n+1,len(boot)-1)]-boot[n])*(i-n)
        result['endpoints'][stage+'_'+endpoint]={'blocks':blocks,'point_ms':statistics.median(savings),'ci_ms':[q(.025),q(.975)],'A_values_ms':[value(x) for x in rows if x['configuration']=='A'],'B_values_ms':[value(x) for x in rows if x['configuration']=='B']}
s=result['endpoints']['Stroke_cpu_ns'];result['stroke_admission']=s['point_ms']>=.1 and s['ci_ms'][0]>0
dependencies=[]
for batch,items in [('capability',cap),('matrix',rows)]:
    for row in items:
        runtime=json.loads((H/batch/f"{row['index']:02}-{row['configuration']}"/'runtime.json').read_text())
        dependencies.append({p:v for p,v in runtime.items() if not p.endswith('/libkritaimage.21.0.0.dylib')})
assert all(v==dependencies[0] for v in dependencies);result['shared_dependencies']=dependencies[0]
(H/'summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('stroke admission',result['stroke_admission'])
for k,v in result['endpoints'].items():print(k,v['point_ms'],v['ci_ms'])
