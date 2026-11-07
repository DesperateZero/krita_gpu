#!/usr/bin/env python3
"""Finite mechanism census, no time attribution or statistical qualification."""
import json
from pathlib import Path
H=Path(__file__).resolve().parent
rows=json.loads((H/'runs-countfix-diagnostic/results.json').read_text())
assert len(rows)==8 and all(r['passed'] for r in rows)
result={}
for side in ['parent','candidate']:
    selected=[r for r in rows if r['side']==side]
    counts={}
    for field in ['projection','stroke_other','all_phases']:
        counts[field]={}
        for name in {c['name'] for r in selected for c in r['counts']}:
            totals=[]
            for r in selected:
                chosen=[c for c in r['counts'] if c['name']==name and
                    (field=='all_phases' or c['stage']==2 and c['projection']==(field=='projection'))]
                totals.append({k:sum(c[k] for c in chosen) for k in ['calls','hits','amount']})
            counts[field][name]={k:sorted({c[k] for c in totals}) for k in totals[0]}
    work=[]
    for r in selected:
        events=r['events'];by_id={e['id']:e for e in events}
        def projection(e):
            while e:
                if e['name']=='proj_merge':return True
                e=by_id.get(e['parent'])
            return False
        work.append({name:sum(e['name']==name and e['stage']==e['end_stage']==2 and projection(e) for e in events)
                     for name in ['proj_merge','operation','seal','cold','private_prepare','private_publish','commit']})
    result[side]=dict(counts=counts,work=work,capacity=[r['capacity'] for r in selected])
(H/'counts-summary.json').write_text(json.dumps(result,indent=2)+'\n')
for side,data in result.items():
    print(side,'work',data['work'])
    for name,value in sorted(data['counts']['projection'].items()):
        if value['amount']!=[0]:print(name,value)
