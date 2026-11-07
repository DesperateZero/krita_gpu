#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent
rows=json.loads((H/'matrix/results.json').read_text());assert len(rows)==4 and all(r['passed'] for r in rows)
names=['inputs','index_size','exact_existing','hint_present','hint_equal','global_comparisons','local_comparisons','global_hit','local_hit','new_values','new_nodes']
processes=[];runtimes=[]
for r in rows:
    path=H/'matrix'/f"{r['index']:02}-{r['configuration']}"/'runtime.json'
    runtimes.append({p:h for p,h in json.loads(path.read_text()).items() if 'libkritaimage.' not in p})
    if r['configuration']=='raw':continue
    grouped={}
    for stage in range(6):
        records=[c for c in r['counts'] if c['stage']==stage]
        for c in records:
            v=dict(zip(names,c['values']))
            assert len(c['values'])==11 and c['site'] in (0,1)
            assert v['exact_existing']+v['new_nodes']==v['inputs']
            assert v['hint_equal']+v['global_hit']+v['local_hit']+v['new_values']==v['new_nodes']
            assert v['hint_equal']<=v['hint_present']<=v['new_nodes']
        totals={name:sum(c['values'][i] for c in records) for i,name in enumerate(names) if name!='index_size'}
        totals.update(calls=len(records),max_index_size=max([c['values'][1] for c in records],default=0),max_comparisons_per_call=max([c['values'][5]+c['values'][6] for c in records],default=0))
        comparisons=totals['global_comparisons']+totals['local_comparisons']
        totals['required_ns_per_comparison_for_0_5ms']=500000/comparisons if comparisons else None
        grouped[str(stage)]=totals
    processes.append(dict(index=r['index'],stages=grouped))
assert all(x==runtimes[0] for x in runtimes)
assert json.loads((H/'matrix/identity-final.json').read_text())['inputs_verified']
result=dict(processes=processes,shared_dependencies=runtimes[0],limits='Counts only; required price is a break-even calculation, not measured cost or a performance confidence interval.',inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [H/'matrix/results.json',H/'PROTOCOL.md',Path(__file__)]})
(H/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
for p in processes:print(json.dumps(p,ensure_ascii=False))
