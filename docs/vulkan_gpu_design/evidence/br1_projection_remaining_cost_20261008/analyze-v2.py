#!/usr/bin/env python3
"""Per-process exclusive accounting; descriptive summaries only, no exclusions."""
import argparse,hashlib,json,statistics
from collections import defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--group',type=int,choices=[1,2,4]);a=p.parse_args()
rows=json.loads((H/('selected-measurement/results.json' if a.group else 'runs-measurement/results.json')).read_text());assert len(rows)==(16 if a.group else 10) and all(r['passed'] for r in rows)
prefix='group-'+str(a.group)+'-' if a.group else 'corrected-'
output=[]
for row in rows:
    events={e['id']:e for e in row['events']};children=defaultdict(list)
    for e in events.values():
        if e['parent']:assert e['parent'] in events;children[e['parent']].append(e)
    for e in events.values():
        assert e['self_cpu_ns']+sum(c['cpu_ns'] for c in children[e['id']])==e['cpu_ns']
        assert e['self_wall_ns']+sum(c['end_ns']-c['start_ns'] for c in children[e['id']])==e['end_ns']-e['start_ns']
    tables={k:defaultdict(lambda:dict(cpu_ns=0,events=0,calls=0)) for k in ['top','cold','metadata','seal','commit','operation','names']}
    total=0;counts=defaultdict(int);cold_names=['base_select','plan_select','claim_entry','cold_storage','descriptor_prepare','backing_reserve','backing_register','pin_writable','private_prepare','provider_allocate']
    for e in events.values():
        if e['stage']!=2 or e['end_stage']!=2:continue
        chain=[];p=e
        while p:chain.append(p['name']);p=events.get(p['parent'])
        if 'proj_merge' not in chain:continue
        counts[e['name']]+=1
        if e['name']=='proj_merge':total+=e['cpu_ns']
        def add(table,name):
            tables[table][name]['cpu_ns']+=e['self_cpu_ns'];tables[table][name]['events']+=1
            tables[table][name]['calls']+=int(e['name']==name)
        group=next((x for x in ['cold','seal','commit','capture','operation'] if x in chain),'merge_other');add('top',group);add('names',e['name'])
        if 'cold' in chain:add('cold',next((x for x in cold_names if x in chain),'cold_other'))
        if 'metadata_local' in chain:add('metadata',next((n for n in chain if n.startswith('meta_')),'metadata_other'))
        if group in ['seal','commit']:
            prefix='MutationSeal' if group=='seal' else 'Commit'
            add(group,next((n for n in chain if n.startswith(prefix)),group+'_other'))
        if group=='operation':add('operation',next((n for n in chain if n.startswith(('PixelOperation','MutationAdapter'))),'operation_other'))
    assert sum(v['cpu_ns'] for v in tables['top'].values())==total
    if row['mode']==3:
        for context in ['cold','seal','commit','operation']:
            assert sum(v['cpu_ns'] for v in tables[context].values())==tables['top'][context]['cpu_ns']
    result=dict(index=row['index'],side=row['side'],mode=row['mode'],group=row.get('group',0),projection_cpu_ns=total,counts=dict(counts),tables={k:dict(v) for k,v in tables.items()},stages=row['stages'],updates=row['sample']['projection_updates'])
    output.append(result)
fine=[r for r in output if r['mode']==3 and (not a.group or r['group']==a.group)];assert len(fine)==4
summary={}
for table in fine[0]['tables']:
    names=set().union(*(r['tables'][table] for r in fine));summary[table]={}
    for name in names:
        vals=[r['tables'][table].get(name,{}).get('cpu_ns',0)/1e6 for r in fine]
        summary[table][name]=dict(median_ms=statistics.median(vals),range_ms=[min(vals),max(vals)],all_ms=vals,call_counts=[r['tables'][table].get(name,{}).get('calls',0) for r in fine])
coarse=[r for r in output if r['side']=='current' and r['mode']==2];up=[r for r in output if r['side']=='upstream']
summary['observation']=dict(coarse_projection_ms=[r['projection_cpu_ns']/1e6 for r in coarse],fine_projection_ms=[r['projection_cpu_ns']/1e6 for r in fine],upstream_projection_ms=[r['projection_cpu_ns']/1e6 for r in up],coarse_stroke_cpu_ms=[next(s['cpu_ns']/1e6 for s in r['stages'] if s['stage']=='Stroke') for r in coarse],fine_stroke_cpu_ms=[next(s['cpu_ns']/1e6 for s in r['stages'] if s['stage']=='Stroke') for r in fine])
(H/(prefix+'accounting.json')).write_text(json.dumps(output,indent=2)+'\n');(H/(prefix+'summary.json')).write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
for table,data in summary.items():
    print(table)
    if table=='observation':print(json.dumps(data));continue
    for n,v in sorted(data.items(),key=lambda kv:-kv[1]['median_ms'])[:20]:print(n,round(v['median_ms'],6),[round(x,6) for x in v['range_ms']],v['call_counts'])
print('all hierarchy and exclusive sums verified; no samples excluded')
