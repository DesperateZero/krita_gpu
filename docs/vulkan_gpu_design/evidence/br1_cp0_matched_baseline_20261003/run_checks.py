#!/usr/bin/env python3
"""Original consumer regressions for the memento dirty-extent repair."""
from pathlib import Path
import concurrent.futures
import argparse
import json
import os
import re
import subprocess

evidence = Path(__file__).resolve().parent
repo = evidence.parents[3] / 'krita'
build = repo / '_build-br0-cpu'
env = dict(os.environ, QT_QPA_PLATFORM='offscreen', KIS_BR1_SEED='12345',
           KIS_TEST_PREFIX_PATH=str(repo / '_install'), KIS_TEST_PLUGIN_PATH=str(build / 'bin'))
parser = argparse.ArgumentParser()
parser.add_argument('--label', default='targeted-01')
parser.add_argument('--full-manager', action='store_true')
args = parser.parse_args()
suites = {
    'manager': ['kis_tiled_data_manager_test', 'testPageStoreHistoryDirtyExtent',
                'testUndoingNewTiles', 'testPurgedAndEmptyTransactions', 'testTransactions',
                'testPurgeHistory', 'testUndoSetDefaultPixel',
                'testPageStorePackedReadSurvivesPublication',
                'testPageStoreIteratorLiveWriteCompatibility'],
    'cpu': ['KisPageStoreCpuMutationTest'],
    'reference': ['KisPageStoreReferenceTest'],
    'freehand': ['FreehandStrokeTest', 'testAutoBrushStroke', 'testPersistentAutoBrushStroke',
                 'testPersistentAutoBrushStrokeCancelled', 'testPersistentAutoBrushStrokeFailure',
                 'testPersistentAutoBrushStrokePressure', 'testPersistentAutoBrushStrokePressureCancelled'],
}
if args.full_manager:
    suites['manager'] = ['kis_tiled_data_manager_test']


def run(job):
    arch, name = job
    command = ['arch', '-' + arch, str(build / 'bin' / suites[name][0]), *suites[name][1:], '-nocrashhandler']
    path = evidence / f'{args.label}-{name}-{arch}.log'
    with path.open('w') as output:
        try:
            code = subprocess.run(command, cwd=repo, env=env, stdout=output,
                                  stderr=subprocess.STDOUT, timeout=240).returncode
        except subprocess.TimeoutExpired:
            code = 'timeout'
    log = path.read_text()
    totals = re.findall(r'^Totals: .+$', log, re.M)
    failures = re.findall(r'^(?:FAIL!|QFATAL).+$', log, re.M)
    passed = code == 0 and len(totals) == 1 and not failures and ', 0 failed, 0 skipped,' in totals[0]
    result = dict(arch=arch, suite=name, command=command, exit_code=code,
                  totals=totals, failures=failures, passed=passed)
    print(json.dumps(result), flush=True)
    return result


records = []
for arch in ['arm64', 'x86_64']:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records += list(pool.map(run, [(arch, name) for name in suites]))
    (evidence / f'{args.label}-results.json').write_text(json.dumps(records, indent=2) + '\n')
raise SystemExit(0 if all(record['passed'] for record in records) else 1)
