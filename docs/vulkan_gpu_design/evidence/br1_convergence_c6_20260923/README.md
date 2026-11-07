# BR1 convergence batch 6 — live state/resource consolidation

This is batch C6, not a new architecture milestone or BR1-PERF acceptance.
The baseline is the dirty working tree after batch 5, not Git HEAD.

## Scope and recovery

`before-source.tar.gz` preserves the entire pre-change PageStore directory, both
changed tests, the architecture checker/generator and all audit JSON, including
the old graph and fixed convergence-start checkpoint. No user files were deleted
outside this scope. Restore individual archived files only after reviewing later
changes; do not overwrite the working tree wholesale.

`state-dispositions.json` records the replaced live APIs and field-level ownership.
Only write-set freeze was test-only; the SourceSet and plan lifecycle were live
code with consumers that were migrated. Zero graph callers are not deletion proof.

Production: +152 / -247 = **-95 lines**, cumulative six-batch **-2,300**.
Tests: +58 / -9; checker: +13 / -4. Generated JSON and documentation are separate.

## Layout and contracts

The same compile_commands entry for KisPageStore.cpp was replayed with
`-fsyntax-only -Xclang -fdump-record-layouts`, separately for arm64 and x86_64,
against the archived source directory and final source. `layout-final.log` records
identical sizes on both: entry 104→104 B, cold Page 888→688 B, write set 160→152 B,
session Private 1296→1048 B. The 992→792 B per-prepared-page sum excludes capacity,
allocator overhead, shared allocations and pixels; it is not a runtime RSS result.

Source references live directly in compact entries, not in prematurely allocated
cold slots. Source-only and removal-only entries do not create cold resources.
The current cancelable guard cycles Prepared→Exposed→Prepared. This is not a
commit-only handoff state machine. Native destruction under full Debt and the
remaining provider/seal, budget, metadata and performance gaps remain open in 84.

## Final verification

Run from `/Users/apple/krita_gpu/krita`:

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

Final logs: `build-final-state.log`, `core-verified.log` (932 cases),
`painter-verified.log` (99), `tiles3-verified.log` (334), `callgraph-final.log`,
`checkpoint.log`, `architecture.log`, `reachability-tests.log`, `negative-gate.log`.
The build is universal; runtime tests ran arm64. Existing linker/fixture warnings
are not test failures. The graph has 1,514 APIs, 13,463 call edges, 14 callbacks,
83 TUs; this remains a CPU-configuration boundary graph, not whole-program proof.

`intermediate-alias-test.log` deliberately retains the failed first new alias
fixture: initial fill's two pins were mistakenly counted in the operation total.
Final assertions use before/after pin deltas. Earlier intermediate source layouts
and graphs are not final acceptance evidence.

`manifest.json` binds the archived evidence, changed sources, audit, compile DB
and final tested binaries by SHA-256. The fixed convergence-start checkpoint was
not regenerated. Architecture fixtures inject retired fields in memory, not into
the user's files; four duplicate fields and two retired tokens were rejected.
