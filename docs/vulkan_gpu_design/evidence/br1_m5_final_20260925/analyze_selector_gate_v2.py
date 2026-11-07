#!/usr/bin/env python3
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PROTOCOL = json.loads((HERE / "selector_protocol_v2.json").read_text())
MANIFEST = json.loads((HERE / "selector-paired-v2/manifest.json").read_text())
OUT = HERE / "selector-analysis-v2.json"
if OUT.exists():
    raise RuntimeError(f"refusing to overwrite {OUT}")
if not MANIFEST.get("completed"):
    raise RuntimeError("selector experiment is incomplete")


def median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    return ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2


state = PROTOCOL["bootstrap_seed"]
def random_index(limit):
    global state
    state ^= (state << 13) & 0xffffffff
    state ^= state >> 17
    state ^= (state << 5) & 0xffffffff
    state &= 0xffffffff
    return int((state / 4294967296) * limit)


results = []
runs = [run for run in MANIFEST["runs"] if run["pair"] is not None]
for bucket in PROTOCOL["required_buckets"]:
    ratios = []
    pair_rows = []
    for pair in range(PROTOCOL["pairs"]):
        values = {}
        rows = [run for run in runs if run["bucket"] == bucket and run["pair"] == pair]
        if len(rows) != 2:
            raise RuntimeError("missing or duplicate pair")
        for run in rows:
            value = run["result"]
            values[run["variant"]] = value["completed_operations"] * 1_000_000_000 / value["wall_ns"]
        ratio = values["candidate"] / values["control"]
        ratios.append(ratio)
        pair_rows.append({"pair": pair, "control_ops_per_second": values["control"],
                          "candidate_ops_per_second": values["candidate"], "ratio": ratio})
    bootstrap = []
    for _ in range(PROTOCOL["bootstrap_resamples"]):
        bootstrap.append(median([ratios[random_index(len(ratios))] for _ in ratios]))
    bootstrap.sort()
    lower_index = int(0.025 * len(bootstrap))
    lower = bootstrap[lower_index]
    results.append({
        "bucket": bucket,
        "paired_median_candidate_control_ratio": median(ratios),
        "one_sided_97_5_percent_lower_bound": lower,
        "required_lower_bound": 0.98,
        "pass": lower >= 0.98,
        "pairs": pair_rows
    })

analysis = {
    "gate": "M5 selector forced-COW matched-control throughput",
    "familywise_confidence": "at least 95% across two required buckets",
    "result": "Pass" if all(row["pass"] for row in results) else "Fail",
    "buckets": results,
    "limits": PROTOCOL["limits"]
}
OUT.write_text(json.dumps(analysis, indent=2) + "\n")
print(json.dumps(analysis, indent=2))
