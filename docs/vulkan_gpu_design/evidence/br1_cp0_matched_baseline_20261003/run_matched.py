#!/usr/bin/env python3
"""Sequential shared-fixture capability and descriptive CP0 pairs."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import statistics
import subprocess
import time

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[3]
CURRENT = ROOT / 'krita'
UPSTREAM = ROOT / 'build/br1-cp0-20261003/upstream-source'
SOURCES = {'current': CURRENT, 'upstream': UPSTREAM}
BUILDS = {'current': CURRENT / '_build-br0-cpu',
          'upstream': ROOT / 'build/br1-cp0-20261003/upstream-build'}
FIXTURE = 'sdk/tests/matched_freehand_baseline.h'
PRESET = 'libs/ui/tests/data/autobrush_300px.kpp'
SHARED_FILES = [FIXTURE, PRESET, 'libs/ui/tests/matched_freehand_baseline_test.cpp',
                'sdk/tests/stroke_testing_utils.cpp']
PLUGINS = {'current': ROOT / 'build/br1-cp0-20261003/current-plugins',
           'upstream': BUILDS['upstream'] / 'bin'}
ARCHES = ['arm64', 'x86_64']
METRICS = ['setup_ns', 'stroke_to_projection_ready_ns', 'pen_up_to_projection_ready_ns',
           'undo_drain_ns', 'redo_drain_ns', 'owner_teardown_ns', 'total_fixture_ns']
parser = argparse.ArgumentParser()
parser.add_argument('--label', required=True)
parser.add_argument('--pairs', type=int, choices=[0, 12], default=0)
args = parser.parse_args()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, data):
    (EVIDENCE / name).write_text(json.dumps(data, indent=2) + '\n')


identity = {side: {name: digest(source / name) for name in SHARED_FILES}
            for side, source in SOURCES.items()}
assert identity['current'] == identity['upstream'], identity
preregister_hash = digest(EVIDENCE / 'preregister.md')
if args.pairs:
    capability = json.loads((EVIDENCE / 'capability-05-results.json').read_text())
    assert capability['passed']
    assert capability['source_identity'] == identity
    assert capability['preregister_sha256'] == preregister_hash

records = []


def run(side, arch, pair=None):
    build = BUILDS[side]
    env = dict(os.environ, QT_QPA_PLATFORM='offscreen', KIS_BR1_SEED='12345',
               KIS_TEST_PREFIX_PATH=str(CURRENT / '_install'),
               KIS_TEST_PLUGIN_PATH=str(PLUGINS[side]))
    for key in list(env):
        if key.startswith('DYLD_'):
            env.pop(key)
    command = ['arch', '-' + arch]
    if not args.pairs:
        command += ['-e', 'DYLD_PRINT_LIBRARIES=1']
    command += [str(build / 'bin/MatchedFreehandBaselineTest'), 'testMatchedCpuBaseline', '-nocrashhandler']
    suffix = '' if pair is None else f'-pair-{pair:02}'
    logfile = EVIDENCE / f'{args.label}-{side}-{arch}{suffix}.log'
    start = time.monotonic()
    with logfile.open('w') as output:
        try:
            code = subprocess.run(command, cwd=SOURCES[side], env=env, stdout=output,
                                  stderr=subprocess.STDOUT, timeout=240).returncode
        except subprocess.TimeoutExpired:
            code = 'timeout'
    log = logfile.read_text()
    samples = re.findall(r'BR1_CP0_JSON (\{[^\n]+\})', log)
    totals = re.findall(r'^Totals: .+$', log, re.M)
    failures = re.findall(r'^(?:FAIL!|QFATAL).+$', log, re.M)
    record = dict(side=side, arch=arch, pair=pair, command=command, log=logfile.name,
                  exit_code=code, process_elapsed_seconds=time.monotonic() - start,
                  totals=totals, failures=failures,
                  sample=json.loads(samples[0]) if len(samples) == 1 else None)
    record['passed'] = (code == 0 and len(totals) == 1 and not failures and
                        ', 0 failed, 0 skipped,' in totals[0] and len(samples) == 1 and
                        '(' + arch + '-little_endian' in log)
    if not args.pairs:
        loaded = []
        for uuid, rawpath in re.findall(r'^dyld\[\d+\]: <([^>]+)> (.+)$', log, re.M):
            path = Path(rawpath).resolve()
            if path.is_file() and str(path).startswith(str(ROOT)):
                loaded.append(dict(path=str(path), uuid=uuid, sha256=digest(path)))
        record['loaded_local_files'] = loaded
        names = {Path(item['path']).name for item in loaded}
        critical = ['libkritaimage.21.0.0.dylib', 'libkritaui.21.0.0.dylib',
                    'kritadefaultpaintops.so', 'kritalcmsengine.so', 'QtCore']
        record['loaded_identity_passed'] = all(name in names for name in critical)
        for item in loaded:
            path = Path(item['path'])
            if path.name.startswith('libkrita') or path.name.startswith('krita') and path.suffix == '.so':
                record['loaded_identity_passed'] &= path.parent == (build / 'bin').resolve()
        record['passed'] &= record['loaded_identity_passed']
    records.append(record)
    print(json.dumps({key: record[key] for key in ['side', 'arch', 'pair', 'passed', 'exit_code']}), flush=True)
    return record


for arch in ARCHES:
    for pair in range(args.pairs or 1):
        order = ['upstream', 'current'] if pair % 2 == 0 else ['current', 'upstream']
        for side in order:
            run(side, arch, pair if args.pairs else None)
        result = dict(source_identity=identity, preregister_sha256=preregister_hash,
                      records=records, passed=all(record['passed'] for record in records))
        write(args.label + '-results.json', result)

hashes = {(record['sample']['blank_sha256'], record['sample']['painted_sha256'])
          for record in records if record['sample']}
passed = all(record['passed'] for record in records) and len(hashes) == 1
if not args.pairs:
    common = [{item['path']: item['sha256'] for item in record['loaded_local_files']
               if Path(item['path']).is_relative_to(CURRENT / '_install')}
              for record in records]
    passed &= bool(common) and all(item == common[0] for item in common)
result['pixel_hashes_identical'] = len(hashes) == 1
result['passed'] = passed
write(args.label + '-results.json', result)
if args.pairs and passed:
    summary = {}
    for arch in ARCHES:
        sides = {side: [record['sample'] for record in records
                        if record['arch'] == arch and record['side'] == side]
                 for side in SOURCES}
        summary[arch] = {metric: {
            'current_mean_ns': statistics.mean(row[metric] for row in sides['current']),
            'upstream_mean_ns': statistics.mean(row[metric] for row in sides['upstream']),
            'current_median_ns': statistics.median(row[metric] for row in sides['current']),
            'upstream_median_ns': statistics.median(row[metric] for row in sides['upstream']),
            'paired_ratio_mean': statistics.mean(current[metric] / upstream[metric]
                for current, upstream in zip(sides['current'], sides['upstream']))
        } for metric in METRICS}
    write(args.label + '-descriptive.json', dict(independent_pairs_per_arch=args.pairs,
        formal_noninferiority=False, canvas_visible=False, metrics=summary))
raise SystemExit(0 if passed else 1)
