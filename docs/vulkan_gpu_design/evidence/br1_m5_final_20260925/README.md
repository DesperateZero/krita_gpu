# BR1/M5 final convergence evidence — 2026-09-25

This directory records the Batch 7 decision required by
[`86_br1_m5_final_convergence_plan_20260925.md`](../../86_br1_m5_final_convergence_plan_20260925.md).
The final source revision is `a0400cf0f7484004dd520e5c03dbc71cbe6827b4`.

## Decision

M5 passes its defined exit gate at the final revision:

- the final arm64 and x86_64 correctness matrices pass;
- the final arm64 and x86_64 Vulkan foundation contract suites pass;
- the architecture gate and all six reachability-tool self-tests pass;
- the tiles3 stress test waits for history and retirement to become idle and verifies that capabilities, pending work, reservations and transient live budget classes settle to zero;
- the preregistered selector v2 matched-control gate passes both required buckets.

This is an M5 decision only. It does not qualify the upstream CPU BR1-PERF matrix, M/K/X/E coverage, tail latency, M6/M7 handoff work, or the complete BR1 optimized version.

## Final correctness matrix

[`correctness-final/identity.json`](correctness-final/identity.json) binds the source, build configuration, graph inputs and binaries by SHA-256. [`correctness-final/manifest.json`](correctness-final/manifest.json) records every run. All rows have zero failed and zero skipped tests.

| Suite | arm64 | x86_64 |
|---|---:|---:|
| `KisCompletionRegistryTest` | 11 | 11 |
| `KisPageStoreFoundationTest` | 28 | 28 |
| `KisPageStorePhysicalClaimTest` | 14 | 14 |
| `KisPageStoreCpuMutationTest` | 577 | 577 |
| `KisPageStoreResidentReadTest` | 33 | 33 |
| `KisPageStoreReferenceTest` | 297 | 297 |
| `KisPageStoreReadBaselineTest` | 45 | 45 |
| `kis_painter_test` | 99 | 99 |
| `kis_tiled_data_manager_test` | 361 | 361 |

The tiles3 runs use `KIS_BR1_SEED=12345`. Their `stressTest` now waits for retirement idle and verifies:

- no outstanding capabilities;
- no pending or deferred historical pages, active history scans, or scheduled reclamation jobs;
- zero reserved bytes in every backing budget class and domain;
- zero live bytes for `ActivePending`, `InFlight`, and `RetirementDebt` in every domain.

The final architecture output is 1452 indexed APIs, 13654 reverse-call edges, 21 single-owner ownership facts, 16 runtime census groups and 19 frozen external intrusion files. The architecture gate and six graph-tool self-tests pass. The 43 statically unreached candidates remain candidates; they were not bulk-deleted or relabeled as dead code.

[`vulkan-compatibility-final/manifest.json`](vulkan-compatibility-final/manifest.json) binds the final contract binary and CMake cache. `KisVulkanFoundationContractsTest` passes 14/14 under both arm64 and x86_64. The initial configuration failure caused by a missing `CMAKE_OSX_DEPLOYMENT_TARGET=12` is retained under `vulkan-compatibility-initial-config-failure/`; only the corrected final run counts as evidence.

## Selector matched-control gate

The first protocol, [`selector_protocol.json`](selector_protocol.json), froze 20 process pairs per required bucket at revision `fe5da2706a`. [`selector-analysis.json`](selector-analysis.json) records a failure:

| Bucket | Paired median candidate/control | One-sided 97.5% lower bound | Required | Result |
|---|---:|---:|---:|---|
| `write-n64-k1-b4` | 0.98149 | 0.97364 | 0.98 | Fail |
| `write-n1024-k16-b4` | 0.99779 | 0.96771 | 0.98 | Fail |

That result was retained and was not reinterpreted. Production selection was then simplified so mutable input is handled by one hot branch before semantic-pending selection. Revision `a0400cf0f7` contains that source change.

Because production changed, [`selector_protocol_v2.json`](selector_protocol_v2.json) preregistered a new fixed experiment before collecting data: 40 independent process pairs per bucket, 750 ms per run, alternating order, no optional stopping, no sample deletion and no replacement. Candidate and control use the same fixture executable bytes; only their captured `libkritaimage` differs. [`selector-identity-v2.json`](selector-identity-v2.json) and the two loader logs record those identities.

[`selector-analysis-v2.json`](selector-analysis-v2.json) records the passing result:

| Bucket | Paired median candidate/control | One-sided 97.5% lower bound | Required | Result |
|---|---:|---:|---:|---|
| `write-n64-k1-b4` | 0.99163 | 0.98685 | 0.98 | Pass |
| `write-n1024-k16-b4` | 1.01092 | 0.99773 | 0.98 | Pass |

Each bucket uses a one-sided 97.5% paired-bootstrap lower bound, which gives at least 95% familywise confidence across the two required buckets by Bonferroni. Raw per-process logs and the full manifest are under `selector-paired-v2/`.

`selector-paired-invalid-control/` preserves an earlier setup rejection: that control changed more than the measured selector decision and the runtime loader check failed, so no result from it was admitted.

## TSAN status

[`tsan-probe/manifest.json`](tsan-probe/manifest.json) shows that the arm64 compiler and runtime can execute a minimal TSAN program. The project was then configured and linked with `-fsanitize=thread`. Completion 11/11, Foundation 28/28 and PhysicalClaim 14/14 finished without a TSAN warning.

The CpuMutation run is **Inconclusive**. Its report starts with a `double lock` warning in the Qt wait path and repeatedly labels both conflicting accesses as holding the same mutex `M0`. The project is instrumented but the dynamically linked Qt synchronization implementation is not, so TSAN cannot observe the complete `QMutex`/`QWaitCondition` unlock-and-relock relation. The retained direct log and process sample are under `tsan-project/`.

This result is neither a race-free pass nor proof of a source race. It is an explicit toolchain gap. The ordinary deterministic interleavings and stress suites remain correctness evidence, not a substitute claim for TSAN.

The project TSAN attempt was made at `fe5da2706a`, before the final selector-only source change. It is therefore supplemental and is not included in the final-revision identity claim.

## Reproduction and integrity

- `run_correctness_final.py` rebuilds and runs the final correctness matrix and architecture checks.
- `run_vulkan_compatibility_final.py` rebuilds and runs the final Vulkan foundation contract matrix.
- `capture_selector_runtime_v2.py`, `run_selector_gate_v2.py` and `analyze_selector_gate_v2.py` implement the frozen selector v2 experiment.
- `run_tsan_probe.py` and `run_tsan_project.py` record the sanitizer probe and project attempt.
- `artifacts.sha256` covers every committed evidence file except itself.

The non-final `correctness/` and `vulkan-compatibility/` directories preserve the complete pre-selector-refactor run at `fe5da2706a`; final status is based only on their `-final` counterparts at `a0400cf0f7`.
