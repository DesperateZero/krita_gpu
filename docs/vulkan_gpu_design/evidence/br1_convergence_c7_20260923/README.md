# BR1 convergence batch 7 — one superseded-overlay lifetime

The comparison is the actual dirty tree after batch 6, not Git HEAD.
This closes one active cleanup protocol, not all C2–C5 work or BR1-PERF.

## Replacement and recovery

Generic replacement now validates its new proof before detaching the old version
to Historical, as native mutation seal already did. Both use HistoryCollector
for retained-root/read/capture/pin/last-use eligibility. Proof failure preserves
the old overlay; detach failure revokes the new proof and uses existing cancel/
abort retry ownership. No handoff or commit-only authority was added.

The superseded-Prepared state-machine branch, Store cleanup method and reverse
read-service callback were live code, not dead code. `protocol-dispositions.json`
preserves their pre-change graph records, call sites and migration decisions.
Request cancellation and failed resolution now trigger historical collection;
failed ReleaseRead keeps the request retryable rather than silently erasing it.
Native multi-page atomic publication remains distinct from generic single-page
publication; provider execution and bounded cancellation are not fully unified.

`before-source.tar.gz` holds all pre-change PageStore sources, the three changed
tests, checker/generator and audit JSON. No source file was deleted wholesale.
Individual old implementations can be recovered from it after reviewing newer
changes; never restore the entire archive over a later working tree.
`changes.patch` records the production/test/checker and three manifest changes.

Production **+38 / -173 = -135**, seven-batch cumulative **-2,435 lines**.
PageStore headers/sources total **31,114** lines. Tests **+123 / -15**;
checker **+2 / -1**. Audit JSON, evidence and documentation are separate.

## Verification

Commands run from `/Users/apple/krita_gpu/krita`:

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

Final logs record universal compilation and arm64 runtime: PageStore/Completion
**1,016** (CPU mutation **570**), Painter **99**, tiles3 **334**, seed 12345.
The new 84 rows cover four old/new native/generic routes, seven borrower/request
lifetimes, and commit/abort/new-proof failure. No FAIL or SAFE ASSERT appeared.
The initial new test used assignment on move-construct-only KisReadLease;
its fixture now holds the lease through unique_ptr, without changing the API.

Fresh Clang graph: **1,512 APIs / 13,525 edges / 13 callbacks / 83 TUs**;
physical-gate production/test callers remain **0/20**. These are boundary-graph
counts for this CPU configuration, not whole-program dead-code certification.
`negative-gate.log` records in-memory rejection of four retired protocol tokens
and the archived stale graph; the fixed convergence-start checkpoint is unchanged.

`manifest.json` binds evidence, changed source/audit files, compile DB and final
tested binaries by SHA-256. Prior evidence directories were not rewritten.
