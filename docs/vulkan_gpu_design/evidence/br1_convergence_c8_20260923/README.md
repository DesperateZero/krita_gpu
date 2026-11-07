# BR1 convergence batch 8 — provider allocation rejection

The baseline is the dirty working tree after batch 7, not Git HEAD. This batch
changes live cleanup code, not code certified as dead.

## Scope and recovery

`before-source.tar.gz` preserves all pre-change PageStore sources, the changed
CPU test, checker/generator and audit JSON. `changes.patch` records only this
batch's source changes; no user source file was removed wholesale. Review later
edits before recovering individual archived files.

Default, alias and generic rejection now use one Store method to retire a
provider replica outside the owner mutex. Generic allocation loss, malformed
provider result and metadata preparation failure use one cleanup exit. The
returned replica must match the target version and selected provider/epoch,
and must not reuse the source allocation, before backing registration or
failure retirement. A provider fault fixture returns another page's live
replica; the request fails without retiring that page or losing its bytes.

Native writable binding cleanup remains distinct because it must release its
pin outside the owner mutex before retiring. This refactor does not unify
normal provider preparation or multi-page atomic seal. The full Debt exit and
remaining C3–C5 work remain open.

Production **+33 / -54 = -21**, eight-batch cumulative **-2,456 lines**.
PageStore headers/sources total **31,093** lines. Tests **+36 / -0**;
evidence, JSON and documentation are separate. `refactor-map.json` records
each old live cleanup site and the replacement; no deleted-function count is
inferred from a line-count difference.

## Verification

From `/Users/apple/krita_gpu/krita`:

```sh
/Users/apple/krita_gpu/.venv/bin/ninja -C _build-br0-cpu -j4 KisPageStoreReferenceTest KisPageStoreResidentReadTest KisPageStoreCpuMutationTest KisPageStoreFoundationTest KisCompletionRegistryTest KisPageStoreReadBaselineTest KisPageStorePhysicalClaimTest kis_tiled_data_manager_test kis_painter_test
env QT_QPA_PLATFORM=offscreen /Users/apple/krita_gpu/.venv/bin/ctest --test-dir _build-br0-cpu -R '^libs-image-(KisPageStore.*|KisCompletionRegistryTest)$' -V -j1
env QT_QPA_PLATFORM=offscreen KIS_TEST_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install KIS_TEST_PLUGIN_PATH=/Users/apple/krita_gpu/krita/_build-br0-cpu/bin arch -arm64 _build-br0-cpu/bin/kis_painter_test
env QT_QPA_PLATFORM=offscreen KIS_BR1_SEED=12345 arch -arm64 _build-br0-cpu/bin/kis_tiled_data_manager_test
python3 build-tools/ci-scripts/tests/test_pagestore_reachability.py -v
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py --write-baseline
python3 build-tools/ci-scripts/check-pagestore-architecture.py
```

Final universal build and arm64 runtime: PageStore/Completion **1,017**
(CPU mutation **571**), Painter **99**, tiles3 **334**, seed 12345; no FAIL or
SAFE ASSERT. The new fault test checks an unrelated current replica remains
readable and its provider bytes/retirement count stay stable.

Fresh Clang graph: **1,513 APIs / 13,529 edges / 13 callbacks / 83 TUs**;
physical gate production/test callers **0/20**. The archived graph is rejected
as stale by the architecture gate. This is a CPU-configuration boundary graph,
not whole-program dead-code or performance certification.

`manifest.json` binds evidence, source/audit files, compile DB and final tested
binaries by SHA-256. The fixed convergence-start checkpoint and prior evidence
directories were not rewritten.
