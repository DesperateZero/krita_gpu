#!/usr/bin/env python3
"""Reanalyse frozen cleanup data; no sampling and no new performance qualification."""
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'br1_cpu_management_cleanup_20261008'
PHASES = ('Stroke', 'Undo', 'Redo', 'Teardown')
inputs = {}


def read(name):
    path = SOURCE / name
    raw = path.read_bytes()
    inputs[name] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def describe(values):
    return dict(values=values, median=statistics.median(values),
                minimum=min(values), maximum=max(values))


upstream = read('runs-upstream/results.json')
upstream_summary = read('upstream-summary.json')
parent_summary = read('parent-summary.json')
original_summary = read('original-summary.json')
observed = read('runs-countfix-diagnostic/results.json')
counts = read('counts-summary.json')
identity = read('delivery-identity.json')
assert len(upstream) == 80 and all(r['passed'] for r in upstream)
assert len(observed) == 8 and all(r['passed'] for r in observed)
assert [r['index'] for r in upstream] == list(range(80))
assert [r['side'] for r in upstream] == ['upstream', 'candidate', 'candidate', 'upstream'] * 20
assert [r['side'] for r in observed] == ['parent', 'candidate', 'candidate', 'parent'] * 2

stages = {}
for phase in PHASES:
    differences = []
    for index in range(0, 80, 2):
        pair = {r['side']: next(s for s in r['stages'] if s['stage'] == phase)
                for r in upstream[index:index + 2]}
        differences.append((pair['candidate']['cpu_ns'] - pair['upstream']['cpu_ns']) / 1e6)
    source_endpoint = upstream_summary['endpoints'][phase + '/cpu_ns']
    assert abs(statistics.median(differences) + source_endpoint['paired_saving_median_ns'] / 1e6) < 1e-9
    stages[phase] = dict(cpu_extra_ms=describe(differences),
                         mean_cpu_extra_ms=statistics.mean(differences),
                         cpu_ratio=source_endpoint['candidate_over_baseline'],
                         cpu_ratio_pointwise_95_ci=source_endpoint['ratio_ci'])
mean_total = sum(row['mean_cpu_extra_ms'] for row in stages.values())
for row in stages.values():
    row['share_of_four_phase_mean_extra'] = row['mean_cpu_extra_ms'] / mean_total

diagnostic = []
for run in observed:
    events = run['events']
    by_id = {e['id']: e for e in events}
    assert len(by_id) == len(events)
    children = defaultdict(list)
    for event in events:
        if event['parent']:
            assert event['parent'] in by_id
            assert by_id[event['parent']]['thread'] == event['thread']
            children[event['parent']].append(event)
    for event in events:
        assert event['self_cpu_ns'] >= 0
        assert event['cpu_ns'] == event['self_cpu_ns'] + sum(c['cpu_ns'] for c in children[event['id']])

    def lineage(event):
        result, seen = [], set()
        while event:
            assert event['id'] not in seen
            seen.add(event['id'])
            result.append(event['name'])
            event = by_id.get(event['parent'])
        return result

    stroke = [e for e in events if e['stage'] == 2]
    assert all(e['end_stage'] == 2 for e in stroke)
    assert all(not e['parent'] or by_id[e['parent']]['stage'] == 2 for e in stroke)
    groups = defaultdict(int)
    contexts = defaultdict(lambda: defaultdict(int))
    event_counts = defaultdict(lambda: defaultdict(int))
    name_self = defaultdict(int)
    for event in stroke:
        chain = lineage(event)
        context = 'projection' if 'proj_merge' in chain else 'stroke_other'
        family = next((n for n in chain if n in ('cold', 'seal', 'commit')), None)
        if family is None:
            family = {'operation': 'operation_residual', 'capture': 'capture',
                      'proj_merge': 'merge_residual'}.get(event['name'], 'other_observed')
        groups[family] += event['self_cpu_ns']
        contexts[context][family] += event['self_cpu_ns']
        event_counts[context][event['name']] += 1
        name_self[event['name']] += event['self_cpu_ns']
    # These spans do not nest one another in these particular processes.
    # Check that inclusive buckets are exclusive of every other bucket above.
    for family in ('cold', 'seal', 'commit'):
        assert groups[family] == sum(e['cpu_ns'] for e in stroke if e['name'] == family)
    covered = sum(groups.values())
    assert covered == sum(e['cpu_ns'] for e in stroke if not e['parent'])
    process_cpu = next(s['cpu_ns'] for s in run['stages'] if s['stage'] == 'Stroke')
    assert process_cpu >= covered
    assert event_counts['projection']['cold'] == 132
    assert event_counts['stroke_other']['cold'] == 76
    assert event_counts['projection']['operation'] == 19
    assert event_counts['stroke_other']['operation'] == 27
    ms = lambda d: {k: v / 1e6 for k, v in sorted(d.items())}
    diagnostic.append(dict(index=run['index'], side=run['side'],
                           groups_ms=ms(groups), contexts_ms={k: ms(v) for k, v in contexts.items()},
                           event_counts={k: dict(sorted(v.items())) for k, v in event_counts.items()},
                           name_self_ms=ms(name_self), covered_ms=covered / 1e6,
                           process_cpu_ms=process_cpu / 1e6, uncovered_ms=(process_cpu-covered) / 1e6,
                           lifecycle_ms=sum(groups[k] for k in ('cold', 'seal', 'commit')) / 1e6,
                           seal_commit_ms=(groups['seal'] + groups['commit']) / 1e6,
                           capture_merge_ms=(groups['capture'] + groups['merge_residual']) / 1e6))

summaries = {}
for side in ('parent', 'candidate'):
    rows = [r for r in diagnostic if r['side'] == side]
    assert len(rows) == 4
    summaries[side] = {key: describe([r[key] for r in rows]) for key in
                       ('covered_ms', 'process_cpu_ms', 'uncovered_ms', 'lifecycle_ms',
                        'seal_commit_ms', 'capture_merge_ms')}
    summaries[side]['groups_ms'] = {key: describe([r['groups_ms'][key] for r in rows])
                                    for key in rows[0]['groups_ms']}

result = dict(schema=1, source_product='704d96e81cf29d16191bc3db8785859d79775e27',
              source_tree='4e7fc164db46c02b968fdd04400b9e4402e289d0',
              source_document_parent='36fb72baf25412fd5f7f7f6c71c487ff93162019',
              input_sha256=inputs,
              method='Post-hoc reanalysis of all frozen rows; no new samples or CIs. Stage CIs copied from original pointwise block analysis. Diagnostic timings include observation costs, do not price upstream differences or removable work.',
              four_phase_mean_extra_ms=mean_total, stages=stages,
              workload_variations=upstream_summary['workload_variations'],
              diagnostic_processes=diagnostic, diagnostic_summary=summaries,
              incremental_stroke_cpu=parent_summary['endpoints']['Stroke/cpu_ns'],
              incremental_stroke_wall=parent_summary['endpoints']['Stroke/wall_ns'],
              original_undo_cpu=original_summary['endpoints']['Undo/cpu_ns'])
assert counts['candidate']['counts']['projection']['find_index']['amount'] == [454]
(HERE / 'summary.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
print('Verified 80 uninstrumented processes and 8 diagnostic processes; no rows excluded.')
print('Candidate diagnostic ms:')
for name, row in summaries['candidate'].items():
    if name != 'groups_ms':
        print(name, round(row['minimum'], 6), round(row['median'], 6), round(row['maximum'], 6))
for name, row in summaries['candidate']['groups_ms'].items():
    print(name, round(row['minimum'], 6), round(row['median'], 6), round(row['maximum'], 6))
