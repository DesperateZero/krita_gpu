# BR1/M5 post-convergence audit evidence

Source: `a0400cf0f7484004dd520e5c03dbc71cbe6827b4`, production tracked source clean.
Decision: reopen the resource and remaining cleanup gates; see [audit 88](../../88_br1_m5_post_convergence_reaudit_20260925.md).

- `probe.cpp` / `probe.log`: real metadata and backing-controller objects. The existing reference-test friend attaches the real budget without changing production code. The finite metadata limit misses page headers and index growth. Reservation microtimings diagnose historical-high-water scanning; they are exploratory, not BR1-PERF qualification.
- `probe-identity.json`: compilation, linkage, source revision and production library hashes. `probe-initial.log` retains the first 64-page exploratory output; its wrapper failed only while hashing an incorrectly named library after execution. The completed probe extended to 128 attempted pages and corrected the hash path.
- `product-probe.cpp` / `product-probe.log`: two real production backends, product RAM 8 MiB, swap/pool 0, separate nonuniform physical pages. Both 6 MiB writes succeed and global tile payload reaches 12 MiB. Close returns it to zero.
- `initial-product-probe.cpp`, `initial-product-probe-identity.json`, `product-probe-previous.log`: the initial uniform-color fill shared each Store's payload and did not exceed the global limit. Preserved to distinguish logical page count from physical bytes. The later probe uses `writeBytes` with varying page/row content. An initial product-probe compilation also required adding the backing-usage type header; it produced no executable result.
- The product probe uses application name `codex-br1-m5-reaudit-budget-probe` and Qt test-mode settings, separate from the user's Krita settings. Its swap-path warning falls back to the temporary directory; swap capacity remains zero and the proof concerns resident RAM.
- `verification.json`, `cpu-mutation-arm64.log`, `reference-arm64.log`: fresh arm64 correctness results, binary digests and source state. 577 + 297 passed, zero failures/skips.
- `architecture.log`, `reachability-self-tests.log`: current structural gate and six tool self-tests pass. Passing those checks does not establish budget completeness or dead-code eligibility.
- `artifacts.sha256`: evidence file checksums.

Rebuild/run either standalone probe from the outer repository:

```sh
python3 docs/vulkan_gpu_design/evidence/br1_m5_reaudit_20260925/run_probe.py
python3 docs/vulkan_gpu_design/evidence/br1_m5_reaudit_20260925/run_probe.py product-probe
```

The helper compiles from the existing CPU Mutation test's compile/link configuration and writes binaries only under `/tmp/codex-br1-reaudit-20260925`. It refuses to overwrite an already retained previous log. Archive existing logs first or use a separate evidence directory for another run.
