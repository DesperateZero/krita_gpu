#!/usr/bin/env python3
from collections import Counter
import json
from pathlib import Path

H=Path(__file__).resolve().parent
results=[]
for run in json.loads((H/'mechanism-results.json').read_text()):
    stages=[];previous={}
    for snapshot in run['snapshots']:
        unique={}
        for device in snapshot['devices']:
            key=device.get('backend')
            if not key:continue
            if key in unique:
                assert all(unique[key]['values'][k]==v for k,v in device.items() if k not in ['role','backend'])
                unique[key]['roles'].append(device['role'])
            else:unique[key]={'roles':[device['role']],'values':{k:v for k,v in device.items() if k not in ['role','backend']}}
        rows=[]
        for key,device in unique.items():
            before=previous.get(key)
            rows.append(dict(backend=key,roles=device['roles'],cumulative=device['values'],
                delta=None if before is None else {k:v-before[k] for k,v in device['values'].items()}))
        stages.append(dict(stage=snapshot['stage'],devices=rows))
        previous={k:v['values'] for k,v in unique.items()}
    results.append(dict(index=run['index'],opt_in_requested=run['opt_in'],projection_updates=run['samples'][0]['projection_updates'],stages=stages))
(H/'mechanism-summary.json').write_text(json.dumps({'records':results,'interpretation':'Sequential phase deltas; aliases deduplicated by actual backend. Only observed live managers. Counts, not timings; opt-in response is not default qualification.'},indent=2)+'\n')
contexts=['prepareWrites','prepareFreshReplica','fillWithPixel','sealImpl','commitLocked','setupProjection','compositeWithProjection','bltFixedImpl']
profiles=[]
for folder in sorted(H.glob('profile-[0-9]*')):
    data=json.loads((folder/'selected-stacks.json').read_text());rows=[]
    for phase in ['Stroke','Undo','Redo','Teardown']:
        selected=[r for r in data if r['phase']==phase]
        for actor in sorted({r['actor'] for r in selected}):
            samples=[r for r in selected if r['actor']==actor]
            rows.append(dict(phase=phase,actor=actor,samples=len(samples),
                exclusive_mechanisms=dict(Counter(r['mechanism'] for r in samples)),
                overlapping_contexts={name:sum(any(name in f for f in s['frames']) for s in samples) for name in contexts}))
    profiles.append(dict(record=folder.name,rows=rows))
(H/'actor-mechanism-summary.json').write_text(json.dumps(profiles,indent=2)+'\n')
