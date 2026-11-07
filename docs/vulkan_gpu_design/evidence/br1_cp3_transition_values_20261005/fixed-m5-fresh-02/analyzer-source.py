"""Frozen block statistic for the unchanged fixed-M5 H0 controls."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

HERE = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument("--round", required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
directory = HERE / a.round
rows = json.loads((directory / "runs.json").read_text())
assert len(rows) == 320
assert all(x["exit_code"] == 0 and x["reaped"] and not x["timed_out"] and x["image_loaded"] for x in rows)
rng = random.Random(260926)
observations = []
for arch in ["arm64", "x86_64"]:
    for k in [1, 16]:
        logs, rates = [], {"m5": [], "current": []}
        for pair in range(40):
            values = {x["variant"]: x["data"][0] for x in rows if x["arch"] == arch and x["K"] == k and x["pair"] == pair}
            pairRates = {v: d["completed_operations"] * 1e9 / d["wall_ns"] for v, d in values.items()}
            for v, rate in pairRates.items(): rates[v].append(rate)
            logs.append(math.log(pairRates["current"] / pairRates["m5"]))
        blocks = [(logs[i] + logs[i+1]) / 2 for i in range(0, 40, 2)]
        resamples = sorted(statistics.median(rng.choices(blocks, k=20)) for _ in range(50000))
        lower = math.exp(resamples[int(.0125 * len(resamples))])
        observations.append(dict(arch=arch, K=k, pairs=40, independent_blocks=20,
            median_completed_rates={v: statistics.median(r) for v, r in rates.items()},
            current_over_m5_throughput=math.exp(statistics.median(blocks)), one_sided_9875_lower=lower,
            minimum_ratio=.98, passes_scoped_nonregression=lower >= .98))
result = dict(observations=observations, scoped_family_pass=all(x["passes_scoped_nonregression"] for x in observations),
    protocol_sha256=hashlib.sha256((directory / "protocol.json").read_bytes()).hexdigest(),
    inputs_verified=json.loads((directory / "identity-final.json").read_text())["inputs_verified"],
    qualification="Original same-source public H0 scanline controls against fixed5173 only; H4 and full M6/CP0 gates remain separate")
with a.output.open("x") as stream: stream.write(json.dumps(result, indent=2)+"\n")
print(json.dumps(result))
