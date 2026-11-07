# BR1/M5 code readiness audit evidence — 2026-09-24

This is a read-only production-code audit. New files are this review and its evidence; no production fix is included.

- `source-sha256.json` binds the reviewed implementation and existing architecture graph/checkpoint.
- `domain_journal_repro.cpp` uses the existing TestProvider/Fixture support copied from CpuMutationTest and actual production libraries. A semaphore pauses one domain snapshot while a newer snapshot is installed. No production implementation is patched. The default mode demonstrates permanent stale domain accounting; passing `metadata` demonstrates an ignored zero MetadataArena budget.
- `build_repro.py` reconstructs the scratch harness under `/tmp/codex-br1-audit-20260924`, using the current compilation database and target link flags. It requires this checkout and its configured build. The source hashes must match for exact reproduction.
- `domain_journal_repro.log`: actual CpuRam backing, ledger CpuRam=0 / Ssd=16384, journal empty, unchanged after another synchronization.
- `metadata_budget_repro.log`: metadata limit=0, two registered pages/two versions, MetadataArena accounting=0, initialization and writes succeed.
- `architecture.log`: current static gate passes; this does not detect either new reproduction.
- `rebuild-business-tests.log`: refreshed the two stale business-test targets before final execution.
- `painter-current.log`: arm64, 99 passed, no FAIL/SAFE ASSERT.
- `tiles3-current.log`: arm64, seed 12345, 334 passed, no FAIL/SAFE ASSERT.

The seven PageStore/Completion ctests were also executed in this audit and all passed. QtTest totals were Foundation 28, Completion 11, Reference 297, ReadBaseline 45, ResidentRead 33, CpuMutation 572, PhysicalClaim 14 (total 1,000). This paragraph records the observed tool result; it is not a retained raw ctest log. Core binaries were already current. Final Ninja dry-run of the core and two business targets reported no work.

Commands used:

```sh
python3 build-tools/ci-scripts/check-pagestore-architecture.py --build-dir _build-br0-cpu
env QT_QPA_PLATFORM=offscreen /Users/apple/krita_gpu/.venv/lib/python3.13/site-packages/cmake/data/bin/ctest --test-dir _build-br0-cpu -R 'Kis(PageStore|CompletionRegistry)' --output-on-failure
env QT_QPA_PLATFORM=offscreen KIS_TEST_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install KIS_TEST_PLUGIN_PATH=/Users/apple/krita_gpu/krita/_build-br0-cpu/bin arch -arm64 _build-br0-cpu/bin/kis_painter_test
env QT_QPA_PLATFORM=offscreen KIS_BR1_SEED=12345 arch -arm64 _build-br0-cpu/bin/kis_tiled_data_manager_test
python3 /tmp/codex-br1-audit-20260924/build_repro.py
env QT_QPA_PLATFORM=offscreen /tmp/codex-br1-audit-20260924/domain_journal_repro
env QT_QPA_PLATFORM=offscreen /tmp/codex-br1-audit-20260924/domain_journal_repro metadata
```

The initial Painter ctest lacked its installation-prefix environment and stopped in resource initialization; it was terminated and replaced by the correctly configured successful run. No PageStore defect is inferred from that attempt. No TSAN, interactive product reproduction, fresh x86_64/Vulkan execution, or formal BR1-PERF qualification is claimed.
