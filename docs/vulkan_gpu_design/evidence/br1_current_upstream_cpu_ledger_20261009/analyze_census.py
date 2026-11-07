#!/usr/bin/env python3
"""Separate main-thread spans, worker CPU, and dedicated reclamation threads."""
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

H = Path(__file__).resolve().parent
rows = json.loads((H/'census/results.json').read_text())
assert len(rows) == 32 and all(r['passed'] for r in rows)


def stats(values):
    return dict(mean=statistics.mean(values), median=statistics.median(values), minimum=min(values), maximum=max(values), values=values)


processes = []
for row in rows:
    stage = next(s for s in row['stages'] if s['stage'] == 'Stroke')
    events = [e for e in row['events'] if e['stage'] == e['end_stage'] == 2]
    by_id = {e['id']: e for e in events}
    roots = [e for e in events if not e['parent']]
    root_by_thread = defaultdict(int)
    coarse, main_parts = defaultdict(int), defaultdict(int)
    job_threads = {e['thread'] for e in events if e['name'].startswith('job_')}
    for event in roots:
        root_by_thread[event['thread']] += event['cpu_ns']
        coarse[event['name']] += event['cpu_ns']
    coarse['uncovered'] = stage['cpu_ns']-sum(e['cpu_ns'] for e in roots)
    assert coarse['uncovered'] >= 0
    for event in events:
        if event['name'].startswith('main_'):
            main_parts[event['name']] += event['self_cpu_ns']
    assert sum(main_parts.values()) == coarse.get('main_stroke', 0)
    record = dict(index=row['index'], block=row['block'], side=row['side'], configuration=row['configuration'],
                  process_cpu_ms=stage['cpu_ns']/1e6, wall_ms=stage['wall_ns']/1e6,
                  coarse_ms={k: v/1e6 for k, v in sorted(coarse.items())},
                  main_parts_ms={k: v/1e6 for k, v in sorted(main_parts.items())},
                  projection_updates=row['sample']['projection_updates'])
    if row['configuration'] == 'census':
        snapshots = row['thread_snapshots']
        assert [s['snapshot'] for s in snapshots] == [0, 1] and all(s['errors'] == 0 for s in snapshots)
        assert snapshots[0]['main_thread'] == snapshots[1]['main_thread']
        main_thread = snapshots[0]['main_thread']
        start = {e['thread']: e for e in row['thread_cpu'] if e['snapshot'] == 0}
        end = {e['thread']: e for e in row['thread_cpu'] if e['snapshot'] == 1}
        assert len(start) == snapshots[0]['count'] and len(end) == snapshots[1]['count']
        born, disappeared = sorted(set(end)-set(start)), sorted(set(start)-set(end))
        roles = defaultdict(int)
        threads = []
        for tid, item in end.items():
            delta = item['cpu_ns']-start.get(tid, {'cpu_ns': 0})['cpu_ns']
            assert delta >= 0
            role = 'main' if tid == main_thread else 'job_workers' if tid in job_threads else item['name'] or 'unnamed'
            roles[role] += delta
            threads.append(dict(thread=tid, name=item['name'], role=role, cpu_ms=delta/1e6,
                                event_root_cpu_ms=root_by_thread.get(tid, 0)/1e6,
                                snapshot_minus_event_ms=(delta-root_by_thread.get(tid, 0))/1e6, born=tid in born))
        outer_cpu = snapshots[1]['after_cpu_ns']-snapshots[0]['before_cpu_ns']
        inner_cpu = snapshots[1]['before_cpu_ns']-snapshots[0]['after_cpu_ns']
        assert snapshots[0]['after_wall_ns'] <= stage['start_ns'] <= stage['end_ns'] <= snapshots[1]['before_wall_ns']
        record.update(thread_roles_ms={k: v/1e6 for k, v in sorted(roles.items())}, threads=threads,
                      born_threads=born, disappeared_threads=disappeared,
                      snapshot_thread_cpu_ms=sum(roles.values())/1e6,
                      snapshot_outer_cpu_ms=outer_cpu/1e6, snapshot_inner_cpu_ms=inner_cpu/1e6,
                      snapshot_outer_minus_stage_cpu_ms=(outer_cpu-stage['cpu_ns'])/1e6,
                      snapshot_inner_minus_stage_cpu_ms=(inner_cpu-stage['cpu_ns'])/1e6,
                      snapshot_thread_minus_stage_cpu_ms=(sum(roles.values())-stage['cpu_ns'])/1e6)
    processes.append(record)

summary = {}
for name in ['control', 'census']:
    selected = [r for r in processes if r['configuration'] == name]
    report = {}
    for side in ['current', 'upstream']:
        sr = [r for r in selected if r['side'] == side]
        assert len(sr) == 8
        report[side] = {k: stats([r[k] for r in sr]) for k in ['process_cpu_ms', 'wall_ms']}
        fields = ['coarse_ms', 'main_parts_ms'] + (['thread_roles_ms'] if name == 'census' else [])
        for field in fields:
            report[side][field] = {k: stats([r[field].get(k, 0) for r in sr]) for k in sorted({k for r in sr for k in r[field]})}
        if name == 'census':
            for field in ['snapshot_outer_minus_stage_cpu_ms', 'snapshot_inner_minus_stage_cpu_ms', 'snapshot_thread_minus_stage_cpu_ms']:
                report[side][field] = stats([r[field] for r in sr])
    extra = defaultdict(list)
    block_extra = []
    for block in range(4):
        batch = [r for r in selected if r['block'] == block]
        assert [r['side'] for r in batch] == ['current', 'upstream', 'upstream', 'current']
        for i in [0, 2]:
            pair = {r['side']: r for r in batch[i:i+2]}
            extra['process_cpu_ms'].append(pair['current']['process_cpu_ms']-pair['upstream']['process_cpu_ms'])
            for field in ['coarse_ms', 'main_parts_ms'] + (['thread_roles_ms'] if name == 'census' else []):
                keys = sorted({k for side in ['current', 'upstream'] for k in report[side][field]})
                for key in keys:
                    extra[field+'/'+key].append(pair['current'][field].get(key, 0)-pair['upstream'][field].get(key, 0))
        block_extra.append({key: statistics.mean(v[-2:]) for key, v in extra.items()})
    report['paired_extra'] = {k: stats(v) for k, v in extra.items()}
    report['block_extra'] = block_extra
    assert abs(sum(v['mean'] for k, v in report['paired_extra'].items() if k.startswith('coarse_ms/'))-report['paired_extra']['process_cpu_ms']['mean']) < 1e-9
    summary[name] = report
result = dict(method='Fixed supplementary 4-block descriptive comparison; Mach live-thread cumulative CPU has a wider endpoint window than Stroke. Do not add snapshot role times to exact event spans as an exact partition.',
              inputs={p: hashlib.sha256((H/p).read_bytes()).hexdigest() for p in ['SUPPLEMENT.md', 'run_census.py', 'census/results.json', 'census/identity-final.json']},
              summary=summary, processes=processes)
extra = summary['census']['paired_extra']
role_sum = sum(v['mean'] for k, v in extra.items() if k.startswith('thread_roles_ms/'))
window_difference = (summary['census']['current']['snapshot_thread_minus_stage_cpu_ms']['mean'] -
                     summary['census']['upstream']['snapshot_thread_minus_stage_cpu_ms']['mean'])
assert abs(role_sum-window_difference-extra['process_cpu_ms']['mean']) < 1e-9
result['thread_difference_reconciliation_ms'] = dict(
    sum_of_role_extra=role_sum, snapshot_minus_stage_difference=window_difference,
    strict_stage_extra=extra['process_cpu_ms']['mean'],
    note='The measured snapshot/strict-stage discrepancy is retained, not removed as a performance correction.')
(H/'census-summary.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
for name, report in summary.items():
    print('\n', name, 'EXTRA', {k: round(v['mean'], 6) for k, v in report['paired_extra'].items()})
    for side in ['current', 'upstream']:
        print(side, 'coarse', {k: round(v['mean'], 6) for k, v in report[side]['coarse_ms'].items()})
        if name == 'census':
            print(side, 'roles', {k: round(v['mean'], 6) for k, v in report[side]['thread_roles_ms'].items()})
            print(side, 'outer extension', report[side]['snapshot_outer_minus_stage_cpu_ms'])
print('Born/disappeared:', [(r['index'], r['born_threads'], r['disappeared_threads']) for r in processes if r['configuration'] == 'census'])
