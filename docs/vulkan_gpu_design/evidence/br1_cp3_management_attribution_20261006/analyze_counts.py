"""Summarize actual calling-thread counters and descriptive ON/OFF perturbation."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
protocol = json.loads((HERE/'count-protocol.json').read_text())
records = json.loads((HERE/'count2-results.json').read_text())
assert len(records) == 8
before = json.loads((HERE/'counts-2-identity-before.json').read_text())
final = json.loads((HERE/'counts-2-identity-final.json').read_text())
assert final['inputs_verified'] and final['hashes'] == before
summary = []
for row in records:
    assert row['exit_code'] == 0 and not row['timed_out'] and row['reaped']
    assert row['image_loaded'] and row['checks_passed'] and len(row['data']) == 1
    d = row['data'][0]
    active = row['mode'] == 'counts'
    assert d['management_counter_active'] == active
    assert len(d['steady_management']) == len(d['first_management']) == 12
    if not active:
        assert not any(d['steady_management']) and not any(d['first_management'])
    expected = d['completed'] * d['K']
    c = d['steady_counts']
    assert c['duplicate_pages'] == c['generations'] == c['sealed_pages'] == expected
    assert c['foreground_copy_bytes'] == expected * 16384
    assert c['sessions'] == c['commits'] == d['completed']
    assert c['preclone_hits'] == c['default_bytes'] == c['payload_bytes'] == 0
    counts = dict(zip(protocol['counter_fields'], d['steady_management']))
    if active:
        assert counts['local_prepare'] == counts['parent_prepare'] == counts['local_settle'] == counts['parent_settle']
        assert counts['control_allocate'] >= counts['local_prepare'] >= counts['storage_owner_allocate']
        assert counts['fits_locked'] >= 2 * counts['local_prepare']
        assert counts['local_release_live'] == counts['parent_release_live']
    summary.append({
        'block':row['block'], 'mode':row['mode'], 'K':d['K'], 'completed':d['completed'],
        'first_counts':dict(zip(protocol['counter_fields'], d['first_management'])),
        'per_operation_counts':{k:v/d['completed'] for k,v in counts.items()},
        'wall_us_per_operation':d['wall_ns']/d['completed']/1000,
        'thread_cpu_us_per_operation':d['thread_cpu_ns']/d['completed']/1000,
    })
pairs = []
for block in (0,1):
    for k in (1,16):
        selected = [r for r in summary if r['block'] == block and r['K'] == k]
        control = next(r for r in selected if r['mode'] == 'control')
        counts = next(r for r in selected if r['mode'] == 'counts')
        pairs.append({'block':block,'K':k,**{metric+'_change_percent':
            100*(counts[metric]/control[metric]-1)
            for metric in ('wall_us_per_operation','thread_cpu_us_per_operation')}})
output = {
    'qualification':'Foreground exact entry counts; no clocks per entry; not causal timing or formal gate',
    'first_attempt':'One control completed pixels but failed actual-library witness; batch stopped, retained and excluded. Launch repaired before fresh 8-process protocol.',
    'records':summary, 'paired_counter_perturbation':pairs,
}
(HERE/'management-counts.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(pairs,indent=2))
