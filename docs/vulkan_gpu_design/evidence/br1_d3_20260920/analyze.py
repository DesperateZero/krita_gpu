#!/usr/bin/env python3
"""Paired slice diagnostics with endpoint/work validation; no NI pass award."""
from pathlib import Path
import json
import random
import statistics

ROOT = Path(__file__).resolve().parent

def record(path):
    text = path.read_text()
    assert "Totals: 3 passed, 0 failed, 0 skipped, 0 blacklisted" in text, path
    rows = [json.loads(line.split("BR1_FIXED ", 1)[1]) for line in text.splitlines() if "BR1_FIXED " in line]
    assert len(rows) == 1, path
    r = rows[0]
    assert r["submitted_page_visits"] == r["loops"] * r["K"]
    assert r["canonical_changed_pages"] == r["logical_changed_pages"] == r["submitted_page_visits"]
    assert r["commits"] == r["loops"]
    return r

def analyze(phase):
    directory = ROOT / phase
    if not (directory / "manifest.json").exists(): return {"status": "NotMeasured"}
    manifest = json.loads((directory / "manifest.json").read_text())
    labels = {"disabled": ("original", "before"), "sampled": ("plain", "sampled"), "paired": ("before", "after")}[phase]
    rows = {}
    for run in manifest["runs"]:
        r = record(directory / run["file"])
        assert r["case"] == run["case"] and r["loops"] == run["loops"]
        assert r["stage_profile"] == (run["label"] == "sampled")
        rows[(run["pair"], run["case"], run["label"])] = r
    cases = sorted({run["case"] for run in manifest["runs"]})
    assert len(rows) == len(cases) * 6 * 2, "incomplete matrix"
    output = {}
    for case in cases:
        pairs, phases = [], {}
        for pair in range(6):
            a, b = (rows[(pair, case, label)] for label in labels)
            for k in ("N", "K", "H", "bpp", "mode", "loops", "canonical_changed_pages", "logical_changed_pages", "adoptions", "write_requests"):
                assert a[k] == b[k], (case, k)
            if phase != "disabled": assert min(a["operation_ms"], b["operation_ms"]) >= 100, case
            pairs.append({"pair": pair, "before_ms": a["operation_ms"], "after_ms": b["operation_ms"],
                          "ratio": b["operation_ms"] / a["operation_ms"], "loops": a["loops"]})
            if phase == "sampled":
                samples = b["sampled_operations"]
                for p in b["phases"]:
                    v = phases.setdefault(p["name"], {"samples": 0, "intervals": 0, "wall_ms": 0, "cpu_ms": 0})
                    v["samples"] += samples
                    for f in ("intervals", "wall_ms", "cpu_ms"): v[f] += p[f]
                if b["mode"] == "real":
                    p = {p["name"]: p for p in b["phases"]}
                    assert p["write_bytes_body"]["intervals"] == samples
                    assert p["write_acquire"]["intervals"] == samples * b["K"]
                assert all(p["name"] != "manifest_export" or p["intervals"] == 0 for p in b["phases"])
        ratios = [p["ratio"] for p in pairs]
        rng = random.Random(937)
        bootstrap = sorted(statistics.median(rng.choices(ratios, k=6)) for _ in range(10000))
        output[case] = {"pairs": pairs, "paired_median_ratio": statistics.median(ratios),
            "paired_median_ratio_bootstrap95": [bootstrap[249], bootstrap[9749]],
            "before_us": statistics.median(p["before_ms"] * 1000 / p["loops"] for p in pairs),
            "after_us": statistics.median(p["after_ms"] * 1000 / p["loops"] for p in pairs),
            "sampled_phases": {name: {**p, "wall_us_per_sampled_operation": p["wall_ms"] * 1000 / p["samples"]}
                               for name, p in phases.items()}}
    return {"status": "MeasuredDiagnostic", "labels": labels, "cases": output}

result = {"qualification": "Paired within-branch slice diagnostic, not upstream M NI, isolated K/E or tail gates",
          "ci_limit": "six pairs; exploratory paired median bootstrap, not preregistered NI margin or full environment-drift control",
          **{phase: analyze(phase) for phase in ("disabled", "sampled", "paired")}}
(ROOT / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({phase: {case: {k: v for k, v in row.items() if k not in ("pairs", "sampled_phases")}
                         for case, row in result[phase].get("cases", {}).items()} for phase in ("disabled", "sampled", "paired")}, indent=2))
