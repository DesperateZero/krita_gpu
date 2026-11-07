# BR1 convergence batch 10 — closing the remaining seven gates

This record binds the concentrated 2026-09-24 pass over the seven entries that
were not closed after batch 9. It records outcomes rather than treating every
intermediate edit as a separate batch. The result is **21 closed / 3 partial /
0 open** across the 24 C2–C5 gates.

## Gate outcomes

| Gate | Before | After | Evidence |
|---|---|---|---|
| C2.8 provider async boundary | open | closed | `KisPageWriteCoordinator::initializeFreshReplica` owns FreshCow selection, source-provider lookup, bridge selection, transfer request, terminal validation and provider-operation consumption. `KisPageStore::acquireWrite` only receives readiness and retains lifecycle validation/install. |
| C3.4 adapter/compat exit | partial | partial | Ten CPU/tiles3 compatibility groups remain production-reachable: tile state/bridge/lease, DM routing, backend admission/anonymous/iterator, iterator base, random accessor and painter operation. None was misclassified as dead code. |
| C3.5 native control cost | open | closed | The CPU guard curve covers N16/N1024, K1/K16 and H0/H32. Per-row counters require page resolutions = completed operations × K, with zero generic requests, default materializations and metadata transitions; binding, snapshot-export and version-input counts remain unchanged. |
| C4.2 incremental domain admission | open | closed | Provider sequence journals and sparse Tiles3 payload observers replace the per-admission scan of every physical backing. Owner synchronization is O(P providers + K coalesced changes), followed by exact-sequence acknowledgement. |
| C4.3 pre-swap admission/pure usage | partial | partial | Swap-out and swap-in now publish reliable Ssd/CpuRam changes outside the tile storage lock; aliases and multiple provider observers are supported. The physical domain still changes before Store admission, so this is reliable post-change accounting, not pre-swap reservation. |
| C4.6 finite Store failure matrix | open | closed | A real Store matrix covers Current atomic rejection, Pending contention, OptionalCache rejection, Ssd/durable rejection and retry after swap-in. Existing tests cover Debt, partial cancellation, rejected retirement, drain and close. |
| C5.5 all-configuration consistency | partial | partial | The full CPU PageStore/Completion set passes on both arm64 and x86_64. The Vulkan-foundation contract also builds and passes on both architectures after replacing one stale completion-source API with canonical whole-ticket validation. The active Vulkan provider remains deliberately fail-closed in BR1, and BR1-PERF qualification remains outstanding. |

## Correctness and control-work evidence

The seven PageStore/Completion targets pass on both architectures, **1,000 /
1,000** assertions each:

| Target | Total |
|---|---:|
| KisCompletionRegistryTest | 11 |
| KisPageStoreFoundationTest | 28 |
| KisPageStorePhysicalClaimTest | 14 |
| KisPageStoreReadBaselineTest | 45 |
| KisPageStoreReferenceTest | 297 |
| KisPageStoreResidentReadTest | 33 |
| KisPageStoreCpuMutationTest | 572 |

The 100 ms CPU-guard control sample produced these representative counts:

- N16/K1/H0: 2,102,896 completed operations.
- N16/K1/H32: 2,194,464 completed operations.
- N1024/K1/H0: 2,101,184 completed operations.
- N1024/K1/H32: 2,061,008 completed operations.
- N1024/K16/H32: 115,504 completed operations and 1,848,064 page resolutions.

These samples establish bounded control work. They are not a throughput or
latency qualification and do not grant BR1-PERF Pass.

The domain-journal regression verifies one exact Ssd change for the expected
physical slot and byte count after swap-out, admission acknowledgement, and a
newer CpuRam change after read-triggered swap-in. The finite-limit regression
uses the real Store and validates cleanup after every rejected path.

The `BUILD_VULKAN_FOUNDATION=ON` configuration rebuilt the current PageStore,
tiles3 and Vulkan sources as a universal target. Its first build identified a
real compatibility intrusion in `KisVulkanSubmissionCoordinator`: it still
called the removed `KisCompletionRegistry::isKnownSource()` API. The caller
now rejects a dependency when canonical `status(ticket)` is `Unknown`, which
validates registry identity, source and ticket value without restoring the old
source-only compatibility API. `KisVulkanFoundationContractsTest` then passed
**14/14 on arm64 and 14/14 on x86_64**.

## Fresh callgraph and architecture ratchet

`generate-pagestore-callgraph.py` indexed **1,381 APIs / 13,355 call edges /
15 callback registrations / 82 translation units**. It reported zero
unresolved edges and physical reservation callers **production/test = 1/6**.
Reachability classification is 950 production-boundary, 249 indirect-review,
139 test-only-review and 43 unreached-review. These classifications do not
authorize automatic deletion.

Before refreshing the source checkpoint, the architecture checker reported
only the 12 intentionally changed source hashes as stale and no intrusion or
ownership violation. After review, the checkpoint was refreshed and the gate
passed again with **21 manifest entries, 18 ownership facts, 16 runtime census
groups and 19 frozen external-intrusion files**.

## Size accounting

PageStore production `.h/.cpp` is **26,759 lines**, versus 26,584 at the
previous record: **+175 lines in this batch**. This increase is recorded as the
cost of the reliable, multi-observer and deadlock-safe backing-domain journal
plus transfer-ownership consolidation. It is not presented as a cleanup win.

The full convergence range remains **33,551 → 26,759 = -6,792 lines
(-20.2%)**. Since batch 9 it is 31,097 → 26,759 = -4,338; after excluding
1,663 lines moved to test support, the in-place production reduction is 2,675
lines. `git diff --check` passes for the touched PageStore, tiles3, tests and
audit files.

## Remaining work

Only three partial gates remain:

1. C3.4 requires direct canonical cursor/operation-scope migration of live
   tile, iterator and painter callers, with old bridge/anonymous/boundary state
   deleted in the same change.
2. C4.3 requires Store admission before swap-out changes the backing domain.
3. C5.5 requires an active Vulkan-provider path beyond BR1's intentional
   fail-closed contract and formal BR1-PERF throughput, latency and memory
   qualification.
