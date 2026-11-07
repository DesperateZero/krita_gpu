#!/usr/bin/env python3
"""Compare exact observed allocation stacks, not total-site-count differences."""
from pathlib import Path
import collections
import hashlib
import json

here = Path(__file__).resolve().parent
previous = here.parent / 'br1_cp1_physical_fault_20261004'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def parse(path):
    sites, usable, traces = {}, {}, collections.defaultdict(list)
    for line in path.read_text().splitlines():
        if not line.startswith(('SITE ', 'USABLE_SITE ', 'TRACE_SITE ')): continue
        kind, rest = line.split(' ', 1)
        row = dict(item.split('=', 1) for item in rest.split())
        if kind == 'SITE': sites[row['id']] = row
        elif kind == 'USABLE_SITE': usable[row['id']] = row
        else: traces[row['id']].append(row)
    return [dict(site=site, usable=usable.get(key, {}), frames=traces[key])
            for key, site in sites.items()
            if site['paid'] == '0' and usable.get(key, {}).get('page') == '1']

def category(row):
    owner = row['site']['owner']
    if 'QStringBuilder' in owner and any('KisPageMutationSession' in f['owner'] for f in row['frames']):
        return 'mutation-error-output'
    if 'KisTiledDataManagerPageStoreBackend9configure' in owner:
        return 'format-number-temporary'
    return None

summaries = []
for arch, old_round in [('arm64', 'reset-ledger-01-arm64'), ('x86_64', 'reset-ledger-02-x86_64')]:
    old = previous / old_round
    new = here / ('observed-' + arch)
    before, after = parse(old / 'run.log'), parse(new / 'run.log')
    result = json.loads((new / 'results.json').read_text())
    identity = json.loads((new / 'identity.json').read_text())
    assert result['exit_code'] == 0 and result['reaped'] and identity['verified']
    assert result['selected_image_loaded'] and result['audit_loaded'] and not result['failures']
    assert any(line.startswith('TABLE_OVERFLOW ') and 'total=0' in line for line in result['heap'])
    for kind in ['HEAP ', 'VM_API ']:
        assert any(line.startswith(kind) and 'label=after-static-destructors ' in line
                   and 'paid_live=0 ' in line for line in result['heap'])
    assert any(line.startswith('USABLE ') and 'paid_excess_peak=0' in line for line in result['heap'])
    removed = [dict(category=category(row), **row) for row in before if category(row)]
    remaining = [row for row in after if category(row)]
    counts = collections.Counter()
    for row in removed: counts[row['category']] += int(row['site']['allocations'])
    assert counts == {'mutation-error-output': 139, 'format-number-temporary': 10}, counts
    assert not remaining, remaining
    detail = dict(arch=arch, previous_round=old_round, current_round=new.name,
        observed_unpaid_page_sites_before=len(before), observed_unpaid_page_sites_after=len(after),
        removed_sites=removed, remaining_sites=remaining, removed_allocations=dict(counts),
        all_observed_unpaid_page_sites_after=after,
        evidence={str(p): sha(p) for folder in [old, new]
                  for p in [folder / 'run.log', folder / 'results.json', folder / 'identity.json']},
        scope='Exact three CPU-path source locations only. Other site-count changes are not credited; this is not a complete external capacity or fault qualification.')
    (here / ('observation-' + arch + '.json')).write_text(json.dumps(detail, indent=2) + '\n')
    summaries.append({k: v for k, v in detail.items()
                      if k not in ['all_observed_unpaid_page_sites_after', 'evidence', 'removed_sites']})
runs = {}
for name in ['normal-arm64', 'normal-x86_64', 'tsan-arm64', 'observed-arm64', 'observed-x86_64']:
    result = json.loads((here / name / 'results.json').read_text())
    identity = json.loads((here / name / 'identity.json').read_text())
    assert result['exit_code'] == 0 and result['reaped'] and not result['failures'] and identity['verified']
    if name.startswith('tsan'):
        assert result['instrumented_core_loaded'] and not result['tsan_warnings']
    runs[name] = result
(here / 'summary.json').write_text(json.dumps(dict(observations=summaries, runs=runs, complete_CP1=False), indent=2) + '\n')
print(json.dumps(summaries))
