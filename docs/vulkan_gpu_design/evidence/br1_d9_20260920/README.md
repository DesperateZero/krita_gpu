# D9 demand-built native read binding cache

Completed diagnostic experiment, not BR1-PERF qualification. See
[the D9 report](../../63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md).
D8 evidence is sealed and must not change. The sole production treatment removes eager read-cache
construction from write/adoption/default/generic-read and discovers/validates
the exact ready CPU replica at first native read. Provider allocation records,
read/write/transfer/retirement gates and captured-root retention stay intact.

Cold diagnostic cache-count inspection does not add hot-path counters or change
SessionStats. New correctness tests cover zero entries after writes/generic reads,
concurrent first readers, cold retained history, reclamation and materialized defaults.
Read provider capabilities are not inferred from an authority-domain label.

Protocol was frozen before collection: 48 buckets x 8 independent process pairs,
384 pairs / 768 timed runs plus 12 loader checks. Paired rate windows are >=200ms;
rotate buckets, alternate variant order, no profiler/concurrent build or tests.
Six groups distinguish D8/D9 warm integration/native/cold, fresh D7/D9 native
controls, inclusive cold phase diagnostics and same-D9 plain/profile perturbation.
No new source/runtime changes during collection; 69 source files and three frozen
runtimes are bound by 407 hashes. The common binary never calls new diagnostic symbols.

Native suite 28, read fixture 33, reference 59, foundation 24, tiled 88, native
fixture 34 and Vulkan contracts 13 passed (Qt totals include init/cleanup).
Architecture check passed. Early build errors are separate from the frozen run;
`build-initial.log` preserves the incorrect new test API call before correction.
Regression clocks are not performance results; GUI/soak/sanitizer were not rerun.

The lazy cache improves native writes against D8, but fresh D7 controls retain
negative offsets. First-read work is transferred into cold read scopes; some warm
read/rect buckets also regress. Phase timing has measurable negative perturbation
in one bucket. All evidence and deviations remain; no self-time attribution,
upstream non-inferiority, event-tail, high-H, full background drain or GPU/UMA Pass.

Recompute into new files; outputs deliberately refuse overwrite:

```sh
node analyze.mjs native-paired/manifest.json /tmp/d9-native-new.json
node verify.mjs
node verify.mjs --archive-only
```

Default verifies current source too; archive-only skips only those 69 live files,
not the frozen snapshots/runtimes. Both require the recorded `/tmp` runtimes and
are not a standalone dependency package. Verification recomputes all six analyses,
checks raw results/counters/pair order/loader identity and D6/D7/D8 seals.
Initial `node verify.mjs --seal` writes verification.json and artifacts.sha256 once;
later verification checks the seal. The Vulkan build hashes are current-at-seal
metadata, not a new test execution. Follow-up treatments need separate evidence.
