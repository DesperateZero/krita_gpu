#!/usr/bin/env python3
"""Record actual API faults and process termination for both frozen VM rounds."""
from pathlib import Path
import hashlib
import json
import re

here = Path(__file__).resolve().parent
output = []
for arch in ['arm64', 'x86_64']:
    directory = here / ('lifecycle-vm-02-' + arch)
    results = json.loads((directory / 'results.json').read_text())
    identity = json.loads((directory / 'identity.json').read_text())
    assert results['actual_exit_code'] == 0 and results['reaped'] and identity['verified']
    assert results['selected_image_loaded'] and results['observer_loaded'] and not results['failures']
    log = (directory / 'run.log').read_text()
    families, mapped = {}, False
    for line in log.splitlines():
        if re.match(r'^0\s+heap-vm-observer', line): mapped = False
        if 'trackedMmap' in line: mapped = True
        if not line.startswith('LIFECYCLE family='): continue
        fields = dict(re.findall(r'(\w+)=([^ ]*)', line))
        family = families.setdefault(fields['family'], dict(trials=0, injected=0, mmap_faults=0))
        family['trials'] += 1
        family['injected'] += int(fields['injected'])
        family['mmap_faults'] += int(mapped and int(fields['injected']) > 0)
        mapped = False
    totals = re.findall(r'^LIFECYCLE_RESULT faults=(\d+) controls=(\d+) absent=(\d+)$', log, re.M)
    assert len(totals) == 1
    faults, controls, absent = map(int, totals[0])
    assert faults == sum(row['injected'] for row in families.values()) and absent == 0
    assert len(families) == controls == 9
    assert 'LIFECYCLE_VM_FINAL paid_vm_live=0 ' in log
    assert any(line.startswith('HEAP label=after-static-destructors ') and 'paid_live=0 ' in line for line in results['summary'])
    assert all('total=0' in line for line in results['summary'] if line.startswith('TABLE_OVERFLOW '))
    output.append(dict(arch=arch, directory=directory.name,
        product_commit='8f84cc8461ca621bc284342dbcdeb6490470b66e',
        results=results, families=families, faults=faults, controls=controls, absent=absent,
        mmap_faults=sum(row['mmap_faults'] for row in families.values()),
        run_log_sha256=hashlib.sha256((directory / 'run.log').read_bytes()).hexdigest(),
        limits='First/last occurrences of observed paid sites on invoking thread; no other-thread, all-occurrence, aggregate hard-bound or dual-native-free-failure qualification.'))
(here / 'lifecycle-vm-summary.json').write_text(json.dumps(output, indent=2) + '\n')
print(json.dumps([{k: row[k] for k in ['arch', 'faults', 'controls', 'absent', 'mmap_faults']} for row in output]))
