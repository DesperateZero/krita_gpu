#!/usr/bin/env python3
"""Check work/identity/completion then summarize process-paired observations."""
from pathlib import Path
import json
import random
import statistics

ROOT = Path(__file__).resolve().parent

def record(path):
    text = path.read_text()
    assert "Totals: 3 passed, 0 failed, 0 skipped, 0 blacklisted" in text, path
    records = [json.loads(s.split("BR1_FIXED ", 1)[1]) for s in text.splitlines() if "BR1_FIXED " in s]
    assert len(records) == 1, path
    r = records[0]
    assert r["canonical_changed_pages"] == r["logical_changed_pages"] == r["loops"] * r["K"]
    assert r["commits"] == r["loops"]
    assert r["operation_ms"] >= 100, (path, r["operation_ms"])
    if "native_write_copy" in r:
        n = r["loops"] * r["K"] if r["mode"] == "real" else 0
        native = n if r["native_write_copy"] else 0
        assert r["native_duplicate_pages"] == native
        assert r["explicit_copy_pages"] == r["default_initialized_pages"] == n - native
        for pages, byte in (("default_initialized_pages", "default_initialized_bytes"),
                            ("explicit_copy_pages", "explicit_copy_bytes"),
                            ("native_duplicate_pages", "native_duplicate_bytes"),
                            ("adopted_pages", "adopted_bytes")):
            assert r[byte] == r[pages] * 4096 * r["bpp"]
        assert r["adopted_pages"] == r["adoptions"]
        assert r["native_foreground_copy_bytes"] == (native - r["native_preclone_hits"]) * 4096 * r["bpp"]
    return r

def analyze(name):
    directory = ROOT / name
    if not (directory / "manifest.json").exists():
        return {"status": "NotMeasured"}
    m = json.loads((directory / "manifest.json").read_text())
    labels = {"scaffold": ("original", "before"), "paired": ("before", "after"), "sampled": ("plain", "sampled")}[m["phase"]]
    rows, identities = {}, {}
    for run in m["runs"]:
        r = record(directory / run["file"])
        assert r["case"] == run["case"] and r["loops"] == run["loops"]
        assert r["stage_profile"] == (run["label"] == "sampled")
        if run["variant"] != "original":
            assert r["native_write_copy"] == (run["variant"] == "after")
        key = (run["pair"], run["case"], run["label"])
        assert key not in rows
        rows[key] = r
        ident = (run["binary_sha256"], run["library_sha256"])
        assert identities.setdefault(run["variant"], ident) == ident
    if m["phase"] == "paired":
        assert identities["before"][0] == identities["after"][0]
        assert identities["before"][1] != identities["after"][1]
    cases = sorted({run["case"] for run in m["runs"]})
    assert len(rows) == len(cases) * 12
    results = {}
    for case in cases:
        pairs, phases, work = [], {}, {}
        for pair in range(6):
            left, right = (rows[(pair, case, label)] for label in labels)
            for key in ("N", "K", "H", "bpp", "mode", "loops", "canonical_changed_pages", "adoptions", "write_requests"):
                assert left[key] == right[key]
            pairs.append({"pair": pair, "before_us": left["operation_ms"] * 1000 / left["loops"],
                          "after_us": right["operation_ms"] * 1000 / right["loops"],
                          "ratio": right["operation_ms"] / left["operation_ms"]})
            for label, r in zip(labels, (left, right)):
                w = work.setdefault(label, {})
                for key in ("default_initialized_bytes", "explicit_copy_bytes", "native_duplicate_bytes", "native_preclone_hits", "native_foreground_copy_bytes", "adopted_bytes"):
                    if key in r: w[key] = w.get(key, 0) + r[key]
            if m["phase"] == "sampled":
                sample_count = right["sampled_operations"]
                assert sample_count == (right["loops"] - 1 - right["stage_sample_offset"]) // right["stage_sample_period"] + 1
                for p in right["phases"]:
                    v = phases.setdefault(p["name"], {"samples": 0, "intervals": 0, "wall_ms": 0, "cpu_ms": 0})
                    v["samples"] += sample_count
                    for key in ("intervals", "wall_ms", "cpu_ms"): v[key] += p[key]
                intervals = {p["name"]: p["intervals"] for p in right["phases"]}
                if right["mode"] == "real":
                    assert intervals["write_provider_prepare"] == sample_count * right["K"]
                    # The fixture omits zero-interval phases from JSON. Cross-
                    # check against the independently asserted payload counts.
                    assert intervals.get("write_provider_transfer", 0) == (0 if right["native_write_copy"] else sample_count * right["K"])
        ratios = [p["ratio"] for p in pairs]
        rng = random.Random(937)
        boot = sorted(statistics.median(rng.choices(ratios, k=6)) for _ in range(10000))
        results[case] = {"pairs": pairs, "paired_median_ratio": statistics.median(ratios),
            "bootstrap95": [boot[249], boot[9749]],
            "before_us": statistics.median(p["before_us"] for p in pairs),
            "after_us": statistics.median(p["after_us"] for p in pairs), "payload_work": work,
            "phases": {key: {**p, "wall_us_per_sampled_operation": p["wall_ms"] * 1000 / p["samples"]} for key, p in phases.items()}}
    return {"status": "MeasuredDiagnostic", "cases": results}

result = {"qualification": "within-branch diagnostic, not isolated M/K, upstream NI or product/tail gate",
          "uncertainty": "six independent process pairs; exploratory median bootstrap, no pre-frozen NI margin",
          **{name: analyze(name) for name in ("scaffold", "paired", "sampled-before", "sampled-after")}}
(ROOT / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({name: {case: {key: r[key] for key in ("before_us", "after_us", "paired_median_ratio", "bootstrap95")}
                       for case, r in result[name].get("cases", {}).items()}
                  for name in ("scaffold", "paired", "sampled-before", "sampled-after")}, indent=2))
