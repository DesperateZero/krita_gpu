# M5 baseline freeze review evidence

Production source: `095193d11a1041c31ba92f218ccaea4a8d4f396f`. This is an audit of the previously accepted build, not a production fix or a new whole-suite pass.

- `default-budget-probe.cpp`, `run_default_probe.py`: use public tiled-manager/storage APIs with a separate Qt test-mode application config (8 MiB resident, zero swap/pool). `default-update.log` reproduces old `defaultPixel()` versus new canonical `readBytes()`. `default-constructor.log` records the successful constructor followed by clone SIGSEGV (`returncode=-11`).
- `default-probe-identity.json`: source/dirty state, full compile/link arguments, loaded build-library and executable hashes, commands and process return codes. The update probe returns zero when the defect is reproduced; zero is not a correctness pass.
- `default-update-loader.log`: separate loader-identity run reproducing the same update mismatch; confirms the actual image library comes from `_build-br0-cpu/bin`.
- `default-constructor-backtrace.log`, `default-constructor-stack.log`: LLDB corroboration of the null default TileData failure; the first batch log stopped at the fault before executing its ordinary post-run `bt`, so the second uses the on-crash backtrace command.
- `debugger-raw-output.json`: lossless LLDB stdout and hashes. The two readable `.log` copies normalize line endings, tabs and trailing whitespace only.
- `index-allocation-probe.cpp`, `run_index_probe.py`: instantiate the production exact-version slot-index template. Override executable `operator new/new[]` only to count calls during `insertReserved()` after successful capacity/token preparation. The fixed-hash-seed 64-insertion result is two allocations totaling 5,120 bytes, with unchanged capacity. This is a component counterexample plus production-call-chain review, not a complete publication allocator trace.
- `index-probe-identity.json`: compile/link/header/executable identity. Initial compilation lacked the arena slot-id include; adding that include corrected the audit harness, without changing production code.
- `review-verification.json`: current source, prior-evidence integrity and current build identity checks, gate/self-test/dry-run results and this review's limited verdict.
- `pre-review-worktree.json`: the four documentation changes that already existed when this review began; preserved before consolidating their status language.
- `artifacts.sha256`: inventory excluding itself.

Reproduction from the outer repository (scripts refuse to overwrite retained run logs):

```sh
python3 docs/vulkan_gpu_design/evidence/br1_m5_baseline_review_20260925/run_default_probe.py
python3 docs/vulkan_gpu_design/evidence/br1_m5_baseline_review_20260925/run_index_probe.py
```

Interpretation and corrective exit conditions are in [90](../../90_br1_m5_baseline_freeze_review_20260925.md); conditional M6–M8/BR1 roadmap is in [91](../../91_br1_m6_to_completion_entry_plan_20260925.md). Previous 2,952 CPU and 28 Vulkan passing totals remain historical results, not new runs or proof against the new counterexamples.
