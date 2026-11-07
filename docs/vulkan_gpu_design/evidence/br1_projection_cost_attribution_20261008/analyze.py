#!/usr/bin/env python3
"""Exact event ancestry and generation lineage; diagnostic CPU is not a gain."""
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

H = Path(__file__).resolve().parent
PHASES = ['proj_clear', 'proj_composite', 'proj_write', 'proj_setup', 'proj_merge']


def observed(row):
    all_events = row['events']
    byid = {e['id']: e for e in all_events}
    assert len(byid) == len(all_events)
    ancestors = {}
    def chain(e):
        if e['id'] not in ancestors:
            parents = chain(byid[e['parent']]) if e['parent'] else []
            ancestors[e['id']] = [e] + parents
        return ancestors[e['id']]
    children = defaultdict(list)
    for e in all_events:
        if e['parent']:
            p = byid[e['parent']]
            assert e['thread'] == p['thread'] and p['start_ns'] <= e['start_ns'] <= e['end_ns'] <= p['end_ns']
            children[e['parent']].append(e)
        assert e['stage'] == e['end_stage']
    for e in all_events:
        assert e['self_cpu_ns'] + sum(c['cpu_ns'] for c in children[e['id']]) == e['cpu_ns']
        assert e['self_wall_ns'] + sum(c['end_ns'] - c['start_ns'] for c in children[e['id']]) == e['end_ns'] - e['start_ns']
    stroke = next(s for s in row['stages'] if s['stage'] == 'Stroke')
    events = [e for e in all_events if e['stage'] == 2]
    assert all(stroke['start_ns'] <= e['start_ns'] <= e['end_ns'] <= stroke['end_ns'] for e in events)
    jobs = [e for e in events if e['name'] == 'job_merge']
    projection = [e for e in events if chain(e)[-1]['name'] == 'job_merge']
    def phase(e):
        for p in chain(e):
            if p['name'] in PHASES: return p['name']
        return 'job_outside_merge'
    def add(target, e, inclusive=False):
        target['events'] += 1
        target['cpu_ns'] += e['cpu_ns'] if inclusive else e['self_cpu_ns']
        target['wall_ns'] += e['end_ns'] - e['start_ns'] if inclusive else e['self_wall_ns']
    bucket = lambda: dict(events=0, cpu_ns=0, wall_ns=0)
    phases, mechanisms, names = defaultdict(bucket), defaultdict(bucket), defaultdict(bucket)
    byphase = defaultdict(lambda: defaultdict(bucket))
    def mechanism(e):
        if any(p['name'] == 'cold_generation' for p in chain(e)): return 'cold_generation_including_payload'
        n = e['name']
        if n.startswith('mutation_seal_'): return 'private_seal'
        if n.startswith('commit_'): return 'canonical_commit'
        if n.startswith(('mutation_adapter_', 'mutation_presence_')): return 'adapter_presence'
        if n == 'pixel_operation_body': return 'pixel_operation_body'
        if n.startswith('pixel_operation_') or n == 'execution_prepare_writes': return 'operation_framing'
        if n == 'clear_page': return 'clear_page_residual'
        if n == 'backend_fill': return 'fill_framing'
        if n.startswith('batch_'): return 'batch_framing'
        if n in ['outer_manager_write','outer_bitblt','source_accessor_setup','capture_read_view']: return n
        return 'other_projection_residual'
    for e in projection:
        add(phases[phase(e)], e)
        add(mechanisms[mechanism(e)], e)
        add(byphase[phase(e)][mechanism(e)], e)
        add(names[e['name']], e)
    total_cpu = sum(e['cpu_ns'] for e in jobs)
    assert sum(v['cpu_ns'] for v in phases.values()) == total_cpu
    assert sum(v['cpu_ns'] for v in mechanisms.values()) == total_cpu
    top_events = [e for e in events if not e['parent']]
    result = dict(index=row['index'], side=row['side'], mode=row['mode'], projection_updates=row['sample']['projection_updates'], stroke=stroke,
        merge_jobs=len(jobs), projection_cpu_ns=total_cpu, projection_summed_wall_ns=sum(e['end_ns']-e['start_ns'] for e in jobs),
        phases=dict(phases), mechanisms=dict(mechanisms), phase_mechanisms={p:dict(m) for p,m in byphase.items()}, exclusive_names=dict(names),
        unassigned_process_cpu_ns=stroke['cpu_ns']-sum(e['cpu_ns'] for e in top_events), checks=row['checks'])
    if row['mode'] != 3: return result
    cold = sorted([e for e in projection if e['name'] == 'cold_generation'], key=lambda e:e['start_ns'])
    clear = [e for e in projection if e['name'] == 'clear_page']
    lineage, price, cold_names = [], defaultdict(bucket), defaultdict(lambda:defaultdict(bucket))
    previous_versions, previous_pages = {}, {}
    for e in cold:
        tags = e['tags']
        store,surface,x,y,base,source,target,transaction,scope,flags = tags
        assert store and surface and target and scope
        key=(store,surface,x,y)
        contents=[c for c in projection if e['id'] in [a['id'] for a in chain(c)]]
        fills=sum(c['name']=='tile_fill_pixel_loop' for c in contents)
        copies=sum(c['name']=='tile_payload_memcpy' for c in contents)
        assert fills+copies==1, (tags,fills,copies)
        route='fill' if fills else 'copy'
        job=chain(e)[-1]['id']
        prior=previous_versions.get((*key,source))
        if prior:
            assert prior['end_ns']<=e['start_ns']
            relation='same_merge_'+prior['phase']+'_to_'+phase(e) if prior['job']==job else 'prior_merge_'+prior['phase']+'_to_'+phase(e)
        elif copies: relation='copy_source_outside_observed_projection'
        else:
            removed=[c for c in clear if tuple(c['tags'][:4])==key and chain(c)[-1]['id']==job and c['end_ns']<=e['start_ns'] and c['tags'][6:9]==[1,1,0]]
            relation='fill_after_full_default_removal' if removed else 'fill_without_observed_removal'
        category=phase(e)+'/'+route+'/'+relation
        add(price[category],e,True)
        for c in contents: add(cold_names[category][c['name']],c)
        item=dict(id=e['id'],job=job,phase=phase(e),route=route,relation=relation,key=list(key),base_generation=base,source_generation=source,target_generation=target,transaction=transaction,scope=scope,flags=flags,
            source_event=prior['id'] if prior else None,previous_page_event=previous_pages.get(key),start_ns=e['start_ns'],end_ns=e['end_ns'],cpu_ns=e['cpu_ns'])
        item['base_facts'] = e.get('facts')
        lineage.append(item)
        previous_versions[(*key,target)]=item
        previous_pages[key]=e['id']
    clear_counts=Counter('skip_default' if e['tags'][8] else 'full_default_removal' if e['tags'][6:8]==[1,1] else 'partial_write' for e in clear)
    composite_work=defaultdict(lambda:dict(calls=0,cpu_ns=0,self_cpu_ns=0))
    for e in projection:
        if e['name']!='proj_composite': continue
        contents=[c for c in projection if any(a['id']==e['id'] for a in chain(c))]
        work=any(c['name'] in ['pixel_operation_body','upstream_tile_write'] for c in contents)
        v=composite_work['with_observed_write' if work else 'without_observed_write']
        v['calls']+=1;v['cpu_ns']+=e['cpu_ns'];v['self_cpu_ns']+=e['self_cpu_ns']
    base_facts=defaultdict(Counter)
    for item in lineage:
        if item['base_facts'] is not None:
            base_facts[item['relation']][str(item['base_facts'])]+=1
    result.update(cold_pages=len(cold), unique_projection_pages=len({tuple(x['key']) for x in lineage}),
        lineage_prices=dict(price), lineage_exclusive_names={k:dict(v) for k,v in cold_names.items()},
        clear_page_counts=dict(clear_counts), phase_calls=dict(Counter(e['name'] for e in projection if e['name'] in PHASES)),
        batch_transactions=[dict(name=e['name'],phase=phase(e),tags=e['tags'],cpu_ns=e['cpu_ns'],self_cpu_ns=e['self_cpu_ns']) for e in projection if e['name'].startswith('batch_')],
        composite_work=dict(composite_work),base_facts_by_lineage={k:dict(v) for k,v in base_facts.items()})
    (H/f"lineage-{row['index']:02}-{row['side']}.json").write_text(json.dumps(lineage,indent=2)+'\n')
    return result


if __name__=='__main__':
    rows=json.loads((H/'measurement/results.json').read_text())
    assert len(rows)==16 and all(r['passed'] for r in rows)
    data=[observed(r) for r in rows]
    coarse=[r for r in data if r['mode']==2]
    differences={}
    for name in PHASES+['job_outside_merge']:
        def vals(side): return [r['phases'].get(name,{}).get('cpu_ns',0) for r in coarse if r['side']==side]
        a,b=vals('current'),vals('upstream')
        differences[name]=dict(current_mean_cpu_ns=statistics.mean(a),upstream_mean_cpu_ns=statistics.mean(b),difference_mean_cpu_ns=statistics.mean(a)-statistics.mean(b),current_range_ns=[min(a),max(a)],upstream_range_ns=[min(b),max(b)])
    result={'interpretation':'fixed ARM diagnostics; coarse actor CPU differences and detailed mechanism/lineage budgets are separate batches, not removable wall or formal CIs',
            'records':data,'coarse_cpu_difference':differences,
            'workload_variations':[[r['index'],r['side'],r['mode'],r['projection_updates']] for r in data if r['projection_updates']!=19]}
    if (H/'detail/results.json').exists():
        detail=json.loads((H/'detail/results.json').read_text())
        assert len(detail)==2 and all(r['passed'] for r in detail)
        result['detail_records']=[observed(r) for r in detail]
        result['detail_workload_variations']=[[r['index'],r['sample']['projection_updates']] for r in detail if r['sample']['projection_updates']!=19]
    original=json.loads((H/'summary-initial.json').read_text())
    assert differences==original['coarse_cpu_difference']
    (H/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    def bounds(values):
        values=list(values)
        return dict(min=min(values),max=max(values),mean=statistics.mean(values))
    full=[r for r in data if r['mode']==3 and r['side']=='current']
    compact={'interpretation':result['interpretation'], 'coarse_cpu_difference':differences,
        'coarse_total_projection_cpu_difference_ns':sum(v['difference_mean_cpu_ns'] for v in differences.values()),
        'initial_lineage_prices':{k:{'count':full[0]['lineage_prices'][k]['events'], 'cpu_ns':bounds(r['lineage_prices'][k]['cpu_ns'] for r in full)} for k in full[0]['lineage_prices']},
        'initial_clear_counts':[r['clear_page_counts'] for r in full],
        'initial_composite_work':[r['composite_work'] for r in data if r['mode']==3],
        'measurement_workload_variations':result['workload_variations']}
    if 'detail_records' in result:
        ds=result['detail_records']
        compact['detail_mechanisms_cpu_ns']={k:bounds([r['mechanisms'][k]['cpu_ns'] for r in ds]) for k in ds[0]['mechanisms']}
        compact['detail_base_facts']=[r['base_facts_by_lineage'] for r in ds]
        compact['detail_workload_variations']=result['detail_workload_variations']
        captures=[]
        for row in detail:
            byid={e['id']:e for e in row['events']};counts=defaultdict(lambda:dict(calls=0,cpu_ns=0))
            for e in row['events']:
                if e['stage']!=2 or e['name']!='capture_read_view':continue
                chain=[e];parent=e
                while parent['parent']:parent=byid[parent['parent']];chain.append(parent)
                if chain[-1]['name']!='job_merge':continue
                phase=next((p['name'] for p in chain if p['name'] in PHASES),'other')
                key=phase+'/selector_'+str(e['tags'][0]);counts[key]['calls']+=1;counts[key]['cpu_ns']+=e['cpu_ns']
            captures.append(dict(counts))
        compact['detail_captures']=captures
    (H/'report.json').write_text(json.dumps(compact,indent=2)+'\n')
    print(json.dumps(differences,indent=2))
    for r in data:
        if r['mode']==3:
            print(json.dumps({k:r[k] for k in ['index','side','projection_cpu_ns','cold_pages','clear_page_counts','lineage_prices']},indent=2))
