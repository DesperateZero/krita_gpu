#!/usr/bin/env python3
"""Fixed-work and opt-in phase diagnostics; NOT upstream M/K/E qualification."""
from collections import defaultdict
import json
import importlib.util
import html
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parent


def records(path, marker):
    text = path.read_text()
    totals = re.search(r"Totals: (\d+) passed, 0 failed, 0 skipped, 0 blacklisted, (\d+)ms", text)
    if not totals:
        raise ValueError(f"Failed or incomplete run: {path.name}")
    rows = [json.loads(line.split(marker, 1)[1]) for line in text.splitlines() if marker in line]
    return rows, int(totals[2])


def fixed_run(path):
    rows, elapsed = records(path, "BR1_FIXED ")
    if len(rows) != 52 or len({r["case"] for r in rows}) != 52:
        raise ValueError(f"Expected complete 52-bucket fixed-work matrix: {path.name}")
    for row in rows:
        assert row["submitted_page_visits"] == row["loops"] * row["K"]
        assert row["canonical_changed_pages"] == row["adoptions"] + row["write_requests"]
        assert row["logical_changed_pages"] == (0 if row["mode"] in ("noop", "identical") else row["loops"] * row["K"])
    return {"file": path.name, "qt_elapsed_ms": elapsed, "cases": {r["case"]: r for r in rows}}


def summarize_fixed(pattern):
    runs = [fixed_run(p) for p in sorted(ROOT.glob(pattern))]
    if not runs:
        return {"status": "NotMeasured"}
    if len(runs) != 5:
        raise ValueError(f"Expected five plain runs: {pattern}")
    result = {}
    for case in runs[0]["cases"]:
        rows = [r["cases"][case] for r in runs]
        if any(r["stage_profile"] for r in rows):
            raise ValueError("Profiled fixture used as plain timing")
        for key in ("N", "K", "H", "loops", "bpp", "submitted_page_visits", "logical_changed_pages", "canonical_changed_pages"):
            assert len({r[key] for r in rows}) == 1, (case, key)
        times = [r["operation_ms"] for r in rows]
        result[case] = {
            **{k: rows[0][k] for k in ("N", "K", "H", "loops", "bpp", "mode", "logical_changed_pages", "canonical_changed_pages")},
            "operation_ms": times, "median_ms": statistics.median(times),
            "sample_stddev_ms": statistics.stdev(times), "range_ms": [min(times), max(times)],
            "median_ns_per_operation": 1e6 * statistics.median(times) / rows[0]["loops"],
            "retained_release_median_ms": statistics.median(r["release_retained_ms"] for r in rows),
        }
    return {"status": "MeasuredDiagnostic", "files": [r["file"] for r in runs], "cases": result}


def stress_runs(pattern):
    rows = []
    for path in sorted(ROOT.glob(pattern)):
        _, elapsed = records(path, "BR1_STAGES ")
        rows.append({"file": path.name, "qt_elapsed_ms": elapsed})
    return {"runs": rows, "median_ms": statistics.median(r["qt_elapsed_ms"] for r in rows) if rows else None}


def stress_profile(path):
    reports, elapsed = records(path, "BR1_STAGES ")
    assert len(reports) == 8
    phases = defaultdict(lambda: {"intervals": 0, "work_items": 0, "wall_ms": 0.0, "cpu_ms": 0.0})
    for report in reports:
        for row in report["phases"]:
            for key in ("intervals", "work_items", "wall_ms", "cpu_ms"):
                if row[key] is None:
                    phases[row["name"]][key] = None
                elif phases[row["name"]][key] is not None:
                    phases[row["name"]][key] += row[key]
    counters, _ = records(path, "BR1_COUNTERS ")
    assert len(counters) == 1
    return {"file": path.name, "qt_elapsed_ms": elapsed,
            "scope": "target manager; phase sums across workers, not E",
            "counters": counters[0], "phases": dict(phases)}


def phase_chart(path, title, source, rows):
    # Do not overlay CPU on wall: clock endpoint costs can make very short
    # profiled CPU intervals larger, and hiding the wall bar would mislead.
    height = 106 + 58 * len(rows)
    maximum = max(max(wall, cpu or 0) for _, wall, cpu in rows) or 1
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1150" height="{height}" viewBox="0 0 1150 {height}">',
             '<rect width="100%" height="100%" fill="#f6f8fb"/>',
             '<g font-family="Arial,sans-serif" fill="#152238">',
             f'<text x="24" y="32" font-size="22" font-weight="bold">{html.escape(title)}</text>',
             f'<text x="24" y="58" font-size="13">{html.escape(source)}; target-manager worker sums, NOT E. Clock overhead included.</text>',
             '<text x="24" y="77" font-size="12">Each pair: upper/light = wall; lower/dark = thread CPU. Times are instrumented intervals, not unbiased self time.</text>']
    for index, (name, wall, cpu) in enumerate(rows):
        top = 96 + index * 58
        parts.append(f'<text x="24" y="{top+18}" font-size="14">{html.escape(name)}</text>')
        for offset, value, color, label in [(0, wall, '#a7c7e7', 'wall'), (19, cpu, '#2474ac', 'CPU')]:
            if value is not None:
                parts.append(f'<rect x="390" y="{top+offset}" width="{600*value/maximum:.3f}" height="14" fill="{color}"/>')
            value_label = f'{value:.3f} s' if value is not None else 'N/A'
            parts.append(f'<text x="1000" y="{top+offset+12}" font-size="12">{label} {value_label}</text>')
    parts.append('</g></svg>')
    path.write_text('\n'.join(parts))


def main():
    result = {"qualification": "Diagnostic only; not paired upstream, NI, K throughput or tail qualification",
              "before_fixed": summarize_fixed("before-fixed-0*.log"),
              "after_fixed": summarize_fixed("after-fixed-0*.log"),
              "before_stress": stress_runs("before-stress-0*.log"),
              "after_stress": stress_runs("after-stress-0*.log")}
    for label in ("before", "after"):
        fixed_path = ROOT / f"{label}-fixed-profile.log"
        if fixed_path.exists():
            result[f"{label}_fixed_profile"] = fixed_run(fixed_path)
        stress_path = ROOT / f"{label}-stress-profile.log"
        if stress_path.exists():
            result[f"{label}_stress_profile"] = stress_profile(stress_path)
    before = result["before_fixed"].get("cases", {})
    after = result["after_fixed"].get("cases", {})
    result["fixed_slice_time_ratios"] = {case: after[case]["median_ms"] / row["median_ms"]
        for case, row in before.items() if case in after}
    # Reuse the historical static plotter, but label the new measured phase
    # intervals explicitly; these are not sampled stack percentages.
    spec = importlib.util.spec_from_file_location("br1_plot", ROOT.parent / "br1_perf_20260920/analyze.py")
    plot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plot)
    for label in ("before", "after"):
        profile = result.get(f"{label}_stress_profile")
        if not profile:
            continue
        for prefix in ("commit_", "adoption_"):
            rows = [(name, row["wall_ms"] / 1000, row["cpu_ms"] / 1000 if row["cpu_ms"] is not None else None)
                    for name, row in profile["phases"].items() if name.startswith(prefix)]
            phase_chart(ROOT / f"{label}-{prefix}phases.svg", f"D2 {prefix.rstrip('_')} measured phase intervals",
                        profile['file'], rows)
    if before and after:
        cases = [f"alias-N{n}-K1-H{h}-B4" for h in (0, 4) for n in (64, 1024, 4096)]
        plot.chart(ROOT / "fixed-n-scaling.svg", "D2-A fixed K=1, BPP=4 alias operation: N/H scaling",
                   "Five plain-run medians; 256 operations/run. Light=before, dark=after. Diagnostic only; NOT upstream NI.",
                   [(case + f" (after {after[case]['median_ns_per_operation']/1000:.2f} us)",
                     before[case]["median_ns_per_operation"] / 1000,
                     after[case]["median_ns_per_operation"] / 1000) for case in cases], "us")
    (ROOT / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"before_stress": result["before_stress"], "after_stress": result["after_stress"],
                      "fixed_buckets": len(before), "compared_buckets": len(result["fixed_slice_time_ratios"])}, indent=2))


if __name__ == "__main__":
    main()
