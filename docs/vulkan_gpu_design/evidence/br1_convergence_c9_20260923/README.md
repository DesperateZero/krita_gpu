# BR1 convergence batch 9 — Fresh preparation and physical identity

This is one archive for the whole selected batch. The baseline is the dirty
working tree after batch 8, not Git HEAD. `before-source.tar.gz` holds the
pre-change PageStore source tree, touched tests, audit scripts and audit JSON;
`changes.patch` is a mechanical source/test delta from that snapshot. Do not
restore the archive wholesale over later user changes.

## Changes and limits

Native CPU mutation and generic write acquisition now call one
`WriteCoordinator::prepareFreshReplica` for FreshPayload, FreshDiscard and
FreshCow provider selection. They retain different access, completion and
transfer boundaries. Their private `BeginPublish -> PublishWrite` transition
is assembled once by `publishPrivateWrite`; native multi-page proof installation
remains atomic and distinct from a single generic lease's seal.

Default materialization and initial canonical byte import now check the
returned replica's exact target version and provider epoch **before** backing
registration and before permitting rejection retirement. Alias, native and
generic paths use the same identity predicate, with the source-allocation
exclusion applied to Fresh writes. A fault fixture returns a live page-1
replica for page-0 generic write, default read and initial byte import.
All three attempts fail without retiring page 1 or changing its pixels or
provider byte count; default read and byte import succeed on retry.

Removed five unconnected write-plan/input/exposure enum values and three
unused private accessors. The handoff values remain a target design in doc 68,
not a running M6/M7 implementation. A fourth apparent zero-call accessor,
`PreparedPublication::backingAuthority`, was **restored** after the full build
found its real template-instantiated caller. This is evidence that the current
CPU Clang graph alone cannot certify dead code, especially templates.

PageStore production `.h/.cpp`: **+88 / -84 = +4 lines**, 31,093 → 31,097.
Nine-batch cumulative reduction: **2,452 lines** from the convergence start.
Tests: **+46 / -4**; no QtTest rows were removed to improve this metric.
This batch does **not** meet doc 84's per-rewrite net-reduction objective.
The shared policy and fail-closed identity checks are useful, but further live
state/protocol removal is needed before C2 or C5 can be called complete.

## Verification

The final universal build succeeded (`build-final.log`). On arm64, all seven
PageStore/Completion test targets passed: **1,017 QtTest totals**, including
CPU mutation **571** (`core-final.log`). Painter **99** and tiles3 **334**
with `KIS_BR1_SEED=12345` passed (`painter-final.log`, `tiles3-final.log`).
No FAIL or SAFE ASSERT occurs in those logs. A writable swap fallback warning
appears; it did not suppress a test failure. `git diff --check` passed.

Reachability self-tests passed (`reachability.log`). Fresh Clang graph:
**1,513 APIs / 13,531 edges / 13 callbacks / 83 TUs**, physical gate
production/test **0/20** (`callgraph-final.log`). Source checkpoint and
architecture gate passed under the previous intrusion ceilings
(`checkpoint.log`, `architecture.log`). The archived pre-change graph was
rejected for seven changed source fingerprints; the fixed convergence-start
checkpoint matches byte-for-byte (`negative-gate.log`). `manifest.json` binds
the final evidence, source/audit files, compile database and tested binaries
to SHA-256 values.

Outstanding: pending/semantic strategy, generic transfer and multi-page
proof seal, finite RetirementDebt destructor exit, incremental backing-domain
admission, C3 read/adapter cleanup, C5 compact representation and BR1-PERF
qualification. Correctness passing is not a throughput claim.
