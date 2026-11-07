#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent
source=H/'pretrace-results.json';rows=json.loads(source.read_text());assert len(rows)==4
reports=[]
for row in rows:
 assert row['passed'] and row['sample']['projection_updates']==19
 stages={s['stage']:s for s in row['snapshots']}
 node=next(d for d in stages['Stroke']['devices'] if d['role']=='node.paint')
 before=next(d for d in stages['Setup']['devices'] if d['role']=='node.paint')
 visits=[v for v in row['visits'] if v['backend']==node['backend']]
 assert len(visits)==27 and all(v['fixed'] and not v['selection'] and v['succeeded'] for v in visits)
 sums={k:sum(v[k] for v in visits) for k in ['P','R','F','C']}
 assert sums==dict(P=76,R=2344,F=5363,C=76)
 observed=node['mutation.writablePinsAcquired']-before['mutation.writablePinsAcquired']
 assert observed==sums['R']+sums['C']==2420
 reports.append(dict(index=row['index'],persistent=row['persistent'],operations=len(visits),sums=sums,
  observed_pins=observed,target_pins_without_required_yields=sums['P']+sums['C'],
  deletable_pairs_without_required_yields=sums['R']-sums['P'],maximum_fragments_per_operation=max(v['F'] for v in visits)))
out=dict(input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),records=reports,
 interpretation='Real sequence supports 2268 fewer pin pairs for the eligible node path with E=0. Necessary yield/progress and actual gain still require product validation. Diagnostic timing is not a performance result.')
(H/'pretrace-summary.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
