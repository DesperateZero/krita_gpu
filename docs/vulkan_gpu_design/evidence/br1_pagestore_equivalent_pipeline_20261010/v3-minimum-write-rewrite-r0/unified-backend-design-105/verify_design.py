#!/usr/bin/env python3
"""Validate the 105 design index and a bounded document-cut semantic model.

This is not a C++ implementation, hardware test, performance sample or general
concurrency proof. Negative controls must expose the design's critical races.
"""
from pathlib import Path
import hashlib
import itertools
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = next(p for p in HERE.parents if (p / 'krita/libs/image/pagestore/native').is_dir())


def index_validation():
    matrix = json.loads((BASE / 'MATRIX.json').read_text())
    design = matrix['unified_backend_extension_105']
    head = subprocess.check_output(['git', '-C', str(ROOT / 'krita'), 'rev-parse', 'HEAD'], text=True).strip()
    assert design['source_commit'] == head
    assert matrix['current_delivery_complete'] is True
    assert design['cpu_delivery_104_remains_complete'] is True
    assert design['implemented_responsibilities'] == 0
    assert design['qualified_responsibilities'] == 0
    assert not design['effect_pricing_allowed']
    assert not any(design['implementation_gates'].values())
    assert design['preimplementation_account']['net_forecast'] is None
    assert {x['id'] for x in design['items']} == {f'UB{i:02}' for i in range(1, 17)}
    mw = {x['id']: x for x in matrix['rows']}
    mapped = set()
    paths = set()
    anchors = 0
    text = (BASE / design['design']).read_text()
    for item in design['items']:
        assert item['id'] in text
        assert item['implementation_state'] == 'not_started'
        assert item['deletion_or_forbidden_residual']
        assert item['acceptance_groups']
        for m in item['original_mw']:
            assert item['id'] in mw[m]['unified_backend_extension_105']['required_items']
            mapped.add(m)
        for anchor in item['source_locations']:
            p = ROOT / anchor['path']
            raw = p.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == anchor['sha256'], anchor['path']
            lines = raw.decode().splitlines()
            assert anchor['symbol'] in lines[anchor['line'] - 1], anchor
            paths.add(anchor['path'])
            anchors += 1
    assert mapped == {f'MW{i:02}' for i in range(1, 13)}
    assert text.count('~~~') % 2 == 0
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' in target or target.startswith('#'):
            continue
        path = target.split('#', 1)[0]
        assert (BASE / path).exists(), target
    return {'source_commit': head, 'responsibilities': 16, 'original_mw_covered': len(mapped),
            'source_anchors': anchors, 'unique_source_files': len(paths),
            'cpu_delivery_unchanged': True, 'implementation_or_gpu_qualification_granted': False}


def cut_trace(order, revision_check=True, surface_guards=True):
    """Two changed surfaces; two independently captured root leases.

    P plans old-root retention; A/B stage original rows; U validates the short
    commit cut and publishes or rolls back. Capture increments retentionRevision.
    Reads of staged surfaces wait for U, without holding the document gate.
    """
    root_epoch = 0
    pages = [0, 0]
    revision = 0
    planned_revision = None
    retain = False
    history = None
    guarded = False
    views = {}
    pending = []
    outcome = None

    def read(reader):
        view = views[reader]
        result = tuple(pages) if view == root_epoch else history
        expected = (view, view)
        return result == expected, {'reader': reader, 'captured_epoch': view,
                                    'actual': result, 'expected': expected}

    for event in order:
        if event == 'P':
            planned_revision = revision
            retain = any(v == 0 for v in views.values())
        elif event in ('A', 'B'):
            guarded = surface_guards
            pages[0 if event == 'A' else 1] = 1
        elif event.startswith('C'):
            views[event[1:]] = root_epoch
            revision += 1
        elif event.startswith('R'):
            if guarded:
                pending.append(event[1:])
            else:
                ok, evidence = read(event[1:])
                if not ok:
                    return False, {'order': order, 'at': event, **evidence}
        elif event == 'U':
            if revision_check and revision != planned_revision:
                pages[:] = [0, 0]
                outcome = 'ReadyRetry'
            else:
                history = (0, 0) if retain else None
                root_epoch = 1
                outcome = 'Committed'
            guarded = False
            for reader in pending:
                ok, evidence = read(reader)
                if not ok:
                    return False, {'order': order, 'at': event, **evidence}
            pending.clear()
    assert not pending and outcome is not None
    assert tuple(pages) == (root_epoch, root_epoch)
    return True, outcome


def cut_model():
    events = ('P', 'A', 'B', 'U', 'C1', 'R1', 'C2', 'R2')
    orders = []
    for order in itertools.permutations(events):
        p = {x: i for i, x in enumerate(order)}
        if p['P'] < p['A'] < p['B'] < p['U'] and p['C1'] < p['R1'] and p['C2'] < p['R2']:
            orders.append(order)
    assert len(orders) == 420
    outcomes = {'Committed': 0, 'ReadyRetry': 0}
    for order in orders:
        ok, evidence = cut_trace(order)
        assert ok, evidence
        outcomes[evidence] += 1
    controls = {}
    for name, args in [('omit_retention_revision', {'revision_check': False}),
                       ('omit_surface_guards', {'surface_guards': False})]:
        failures = [proof for order in orders for ok, proof in [cut_trace(order, **args)] if not ok]
        assert failures, name
        controls[name] = {'counterexamples': len(failures), 'first': failures[0]}
    return {'interleavings': len(orders), 'violations': 0, 'outcomes': outcomes,
            'negative_controls': controls,
            'covered': ['two-surface staged changes', 'two late captures', 'blocked exact reads',
                        'all-or-nothing root cut', 'Ready retained after revision mismatch'],
            'not_covered': ['C++ atomics or locking', 'budget settlement', 'physical services',
                            'root GC/default/enumeration', 'concurrent writers',
                            'release interleavings', 'hardware failure', 'performance']}


def main():
    result = {'kind': 'design_index_and_bounded_semantic_model', 'index': index_validation(),
              'document_cut_model': cut_model(),
              'production_code_changed': False, 'performance_processes': 0,
              'gpu_or_uma_execution': False, 'machine_upper_bound_proven': False,
              'status': 'passed_with_explicit_model_scope'}
    output = HERE / 'DESIGN_VALIDATION.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'source_anchors': result['index']['source_anchors'],
                      'model_interleavings': result['document_cut_model']['interleavings'],
                      'negative_controls_detected': list(result['document_cut_model']['negative_controls']),
                      'output': str(output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
