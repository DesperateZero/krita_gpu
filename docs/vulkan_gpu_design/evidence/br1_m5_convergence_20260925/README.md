# BR1/M5 convergence repair evidence

This directory records the post-fix probes for the findings in audit 88.

- `product-probe.cpp`: two real production backends share an 8 MiB process tile-resident limit. A 6 MiB first write succeeds; the second 6 MiB write is rejected, cleanup completes, and process tile residency remains within the limit and returns to zero after close.
- `probe.cpp`: a finite metadata limit admits exactly the capacity already charged and rejects the first owning-capacity growth (page 65). It also measures reservation cost after historical slot high-water marks to verify reserve/release no longer scans retired slots.
- `*-identity.json`: exact compile/link arguments, source state and hashes for the source, executable and loaded production library.
- `protocol.json`, `run_correctness.py`, `correctness/`: one source-current run of the PageStore, Painter and tiles3 suites on arm64 and x86_64, plus the architecture gate and its six self-tests.
- `protocol-final.json`, `run_correctness_final.py`, `correctness-final/`: the same matrix rebound to the final selector-specialized source revision.
- `selector_protocol.json`, `selector-control.patch`, `capture_selector_runtime.py`, `run_selector_gate.py`, `analyze_selector_gate.py`: frozen matched-control selector gate for the post-reaudit production commit. The output is retained in `selector-paired/` and `selector-analysis.json`.
- `selector_protocol_balanced.json` and the `*_balanced.py` runners: fresh follow-up protocol frozen after the first analysis exposed alternating run-order bias. Adjacent opposite-order pairs form 20 geometric-mean blocks; no first-run sample is reused. Results are retained in `selector-paired-balanced/` and `selector-analysis-balanced.json`.
- `verify_selector_machine_equivalence.py`, `selector-machine-equivalence.json`: after both candidate experiments failed K=1, production adopted the measured control branch. The proof compares the complete arm64 and x86_64 `__TEXT,__text` disassembly of final production with that captured control; both are byte-for-byte identical after removing `otool`'s input-path line.
- `vulkan-arm64.log`, `vulkan-x86_64.log`, `verification.json`: final-source Vulkan foundation compatibility on both architectures and a compact identity/result summary for the complete convergence evidence.
- `artifacts.sha256`: SHA-256 inventory of every retained evidence artifact except the inventory itself.

Run from the outer repository:

```sh
python3 docs/vulkan_gpu_design/evidence/br1_m5_convergence_20260925/run_probe.py
python3 docs/vulkan_gpu_design/evidence/br1_m5_convergence_20260925/run_probe.py product-probe
```

The helper writes executables only under `/tmp/codex-br1-reaudit-20260925` and refuses to overwrite retained logs.
