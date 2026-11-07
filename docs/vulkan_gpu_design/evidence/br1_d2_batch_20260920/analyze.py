#!/usr/bin/env python3
"""D2-B owner-gated prepared metadata publication: diagnostic, not NI gates."""
import importlib.util
import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("d2", ROOT.parent / "br1_d2_20260920/analyze.py")
d2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d2)
d2.ROOT = ROOT

result = {
    "qualification": "CPU/CpuRam diagnostic only, not upstream M NI, isolated K, product E or tails",
    "before_fixed": d2.summarize_fixed("before-fixed-0*.log"),
    "after_fixed": d2.summarize_fixed("after-fixed-0*.log"),
    "before_stress": d2.stress_runs("before-stress-0*.log"),
    "after_stress": d2.stress_runs("after-stress-0*.log"),
}
for name in ("before_stress", "after_stress"):
    assert len(result[name]["runs"]) == 5
before = result["before_fixed"]["cases"]
after = result["after_fixed"]["cases"]
assert set(before) == set(after)
for case in before:
    for field in ("N", "K", "H", "bpp", "mode", "loops", "canonical_changed_pages", "logical_changed_pages"):
        assert before[case][field] == after[case][field], (case, field)
result["fixed_slice_time_ratios"] = {
    case: after[case]["median_ms"] / before[case]["median_ms"] for case in before
}
result["stress_slice_time_ratio"] = result["after_stress"]["median_ms"] / result["before_stress"]["median_ms"]
result["after_fixed_profile"] = d2.fixed_run(ROOT / "after-fixed-profile.log")
result["after_stress_profile"] = d2.stress_profile(ROOT / "after-stress-profile.log")
result["refined_fixed"] = d2.summarize_fixed("refined-fixed-0*.log")
result["refined_stress"] = d2.stress_runs("refined-stress-0*.log")
assert len(result["refined_stress"]["runs"]) == 5
refined = result["refined_fixed"]["cases"]
assert set(refined) == set(before)
for case in before:
    for field in ("N", "K", "H", "bpp", "mode", "loops", "canonical_changed_pages", "logical_changed_pages"):
        assert before[case][field] == refined[case][field], (case, field)
result["refined_slice_time_ratios"] = {case: refined[case]["median_ms"] / before[case]["median_ms"] for case in before}
result["refined_stress_ratio"] = result["refined_stress"]["median_ms"] / result["before_stress"]["median_ms"]
result["refined_fixed_profile"] = d2.fixed_run(ROOT / "refined-fixed-profile.log")
result["refined_stress_profile"] = d2.stress_profile(ROOT / "refined-stress-profile.log")
for case in result["refined_fixed_profile"]["cases"].values():
    phases = {p["name"]: p for p in case["phases"]}
    assert phases.get("manifest_export", {}).get("intervals", 0) == 0
    assert phases.get("commit_root_publication", {}).get("intervals", 0) == case["commits"]
    assert phases.get("commit_metadata_apply", {}).get("work_items", 0) == case["canonical_changed_pages"]
# This profile is historical and has a different phase boundary at root
# publication. Its provenance is retained; it is NOT a freshly paired before.
result["historical_before_profile"] = d2.stress_profile(ROOT.parent / "br1_d2_20260920/after-stress-profile.log")
result["historical_before_profile"]["source"] = "../br1_d2_20260920/after-stress-profile.log"
for label in ("after", "refined"):
    profile = result[f"{label}_stress_profile"]
    for prefix in ("commit_", "adoption_"):
        rows = [(name, row["wall_ms"] / 1000, row["cpu_ms"] / 1000 if row["cpu_ms"] is not None else None)
                for name, row in profile["phases"].items() if name.startswith(prefix)]
        d2.phase_chart(ROOT / f"{label}-{prefix}phases.svg", f"D2-B {label} " + prefix.rstrip("_") + " measured intervals",
                       profile["file"], rows)
cases = [f"{mode}-N4096-K{k}-H{h}-B4" for mode in ("alias", "real") for k in (1, 16) for h in (0, 4)]
rows = [(case, before[case]["median_ns_per_operation"] / 1000, refined[case]["median_ns_per_operation"] / 1000)
        for case in cases]
maximum = max(max(b, r) for _, b, r in rows)
height = 105 + 58 * len(rows)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1150" height="{height}">',
       '<rect width="100%" height="100%" fill="#f6f8fb"/><g font-family="Arial,sans-serif" fill="#152238">',
       '<text x="24" y="32" font-size="22" font-weight="bold">D2-B fixed-work operation medians (N=4096, BPP=4)</text>',
       '<text x="24" y="58" font-size="13">Five plain runs, 256 operations/run; diagnostic only, NOT upstream NI. Values: us/operation.</text>',
       '<text x="24" y="77" font-size="13">Upper/light=before; lower/dark=refined. Separate bars preserve regressions as well as improvements.</text>']
for i, (name, b, r) in enumerate(rows):
    y = 96 + i * 58
    svg.append(f'<text x="24" y="{y+18}" font-size="14">{html.escape(name)}</text>')
    for offset, value, color, label in ((0, b, '#a7c7e7', 'before'), (19, r, '#2474ac', 'refined')):
        svg.append(f'<rect x="330" y="{y+offset}" width="{550*value/maximum:.3f}" height="14" fill="{color}"/>')
        svg.append(f'<text x="900" y="{y+offset+12}" font-size="12">{label} {value:.3f} us</text>')
    svg.append(f'<text x="1040" y="{y+20}" font-size="12">{r/b:.3f}x</text>')
svg.append('</g></svg>')
(ROOT / "fixed-work-comparison.svg").write_text('\n'.join(svg))
(ROOT / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({
    "before_stress": result["before_stress"], "after_stress": result["after_stress"],
    "stress_ratio": result["stress_slice_time_ratio"],
    "fixed_buckets": len(before), "fixed_ratios": result["fixed_slice_time_ratios"],
    "profile_elapsed_ms": profile["qt_elapsed_ms"],
    "counters": profile["counters"], "phases": profile["phases"],
    "refined_stress": result["refined_stress"], "refined_stress_ratio": result["refined_stress_ratio"],
    "refined_ratios": result["refined_slice_time_ratios"],
}, indent=2))
