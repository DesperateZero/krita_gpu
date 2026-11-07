# D8 native resident read and true-write regression

This is a versioned diagnostic slice, not BR1-PERF qualification. See
[the report](../../62_br1_native_resident_read_and_write_cost_20260920.md).

- Frozen D7/D8 source/runtime identities: `identity.json`, `source/`, tracked
  image patch, untracked image archive and CMake cache. The `/tmp` runtime is
  local execution evidence, not a portable dependency package.
- Protocol frozen before collection: 18 integration and 5 native-control
  buckets, 8 independent alternating process pairs each (184 pairs), 200 ms
  completed windows; 368 timed runs and 4 library-loader checks, no profiler.
- The common read executable only calls old APIs. Expected requests/page is
  explicitly 1 for D7 and 0 for D8. Warm payload/binding, operation capture and
  release included; setup/history close reported separately, not full drain.
- `generic-counter-contract-counterexample.log/json` runs the old D7 fixture
  against the D8 library to preserve its six obsolete generic-count failures.
- Native lifecycle suite: 24 passed; reference 59, foundation 24, read fixture
  21, tiled 88, native fixture 34 and Vulkan contracts 13. Totals include Qt
  init/cleanup. Initial and final logs remain distinct.
- New-facade read throughput improves; native true write regresses 2.3–4.8%.
  All pairs are kept. Eager binding maintenance is a research hypothesis, not
  a measured allocation/lock self-time attribution. Lazy-cache follow-up must
  create new evidence and must not modify this slice.

Recompute to a new output file (existing files are deliberately not replaced):

```sh
node analyze.mjs integration-paired/manifest.json /tmp/d8-integration-new.json
node analyze.mjs native-paired/manifest.json /tmp/d8-native-new.json
node verify.mjs
```

Default verification also checks the current source against the frozen slice.
After later code changes, `node verify.mjs --archive-only` verifies the frozen
snapshot/runtime/logs without claiming that the new working tree is this version.
Both modes still require the recorded `/tmp` runtimes; archive-only does not
make this a self-contained portable package. `verification.json` records the
one-time live-source check and current Vulkan build hashes, not a new test run.
`artifacts.sha256` seals this directory; verification checks existing seals and
the unchanged D6/D7 archives. Initial sealing uses `node verify.mjs --seal` and
refuses to overwrite either seal output. Recomputed analyses must be byte-identical.
Cold binding self, fixed-work/tail, high-H/concurrent performance, full drain,
upstream non-inferiority and GPU/UMA product qualification remain unproven.
