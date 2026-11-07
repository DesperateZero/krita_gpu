"""Reproduce frozen paired analysis without changing raw samples."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

p = argparse.ArgumentParser()
p.add_argument("--round", default="latency-paired")
p.add_argument("--output", required=True, type=Path)
a = p.parse_args()
HERE = Path(__file__).resolve().parent / a.round
runs = json.loads((HERE / "runs.json").read_text())
rng = random.Random(12345)
results = []
for arch in ["arm64", "x86_64"]:
    for k in [1, 16]:
        pairs, fresh, handoff = [], [], []
        for pair in range(40):
            values = {r["variant"]: r["median_ns"] for r in runs
                if r["arch"] == arch and r["K"] == k and r["pair"] == pair}
            fresh.append(values["fresh"])
            handoff.append(values["handoff"])
            pairs.append(math.log(values["fresh"] / values["handoff"]))
        median = math.exp(statistics.median(pairs))
        bootstrap = sorted(statistics.median(rng.choices(pairs, k=40)) for _ in range(20000))
        lower = math.exp(bootstrap[int(.0125 * len(bootstrap))])
        upper = math.exp(bootstrap[int(.9875 * len(bootstrap))])
        threshold = .2 if k == 1 else .3
        results.append(dict(arch=arch, K=k, pairs=40,
            fresh_median_ns=statistics.median(fresh), handoff_median_ns=statistics.median(handoff),
            fresh_over_handoff=median, latency_reduction=1-1/median,
            one_sided_9875_lower_reduction=1-1/lower,
            interval_975=[1-1/lower, 1-1/upper], required_reduction=threshold,
            passes_measured_scoped_gate=(1-1/lower) >= threshold))
result = dict(protocol_sha256=hashlib.sha256((HERE / "protocol.json").read_bytes()).hexdigest(),
    observations=results, family_pass=all(r["passes_measured_scoped_gate"] for r in results),
    inputs_verified=json.loads((HERE / "identity-final.json").read_text())["inputs_verified"],
    qualification="current controlled-selector latency only; no formal M6/stroke E/fixed-M5 nonregression qualification")
with a.output.open("x") as stream:
    stream.write(json.dumps(result, indent=2) + "\n")
