#!/usr/bin/env python3
"""D1 diagnostic summaries, not paired-upstream noninferiority qualification.

Exclusive implementation-path counts are non-waiting worker stack occupancy,
not CPU time. They complement, and must not be added to, analyze.py categories.
"""
import json
from collections import Counter
from pathlib import Path
import re
import statistics


ROOT = Path(__file__).resolve().parent


def plain_runs(pattern):
    rows = []
    for path in sorted(ROOT.glob(pattern)):
        source = path.read_text()
        match = re.search(r"Totals: \d+ passed, 0 failed, 0 skipped, 0 blacklisted, (\d+)ms", source)
        if not match:
            raise ValueError(f"Incomplete or failed plain run: {path.name}")
        rows.append({"file": path.name, "qt_ms": int(match[1]),
                     **{name: float(re.search(rf"^{name} ([\d.]+)$", source, re.M)[1])
                        for name in ("real", "user", "sys")}})
    values = [r["qt_ms"] for r in rows]
    return {"runs": rows, "n": len(rows),
            "median_qt_ms": statistics.median(values) if values else None,
            "range_qt_ms": [min(values), max(values)] if values else None,
            "sample_stddev_qt_ms": statistics.stdev(values) if len(values) > 1 else None}


def stage(joined):
    # First match owns each leaf. These are implementation paths, not a claim
    # that source-level phase endpoints were instrumented.
    if "validateInvariants" in joined:
        return "full state invariant validation"
    if "KisPageStateMachine::applyImpl" in joined:
        return ("transition under metadata apply" if
                "KisPageMetadataCoordinator::apply" in joined else
                "transition outside metadata apply (includes preflight)")
    for symbol, label in (
        ("sealPreparedPage", "proof sealing excluding nested state validation"),
        ("validatePreparedPage", "proof revalidation excluding nested state validation"),
        ("reachablePageVersions", "root/history reachability"),
        ("KisImageEpochReferenceModel::prepare", "epoch prepare/change-set work"),
        ("KisImageEpochReferenceModel::commit", "epoch commit/root work"),
        ("KisPageMetadataCoordinator::pageSnapshot", "metadata snapshot/lookup"),
        ("KisTiles3PageReplicaProvider::retire", "provider retirement"),
        ("adoptSynchronousHostReplica", "provider synchronous adoption"),
        ("rebuildPageStoreIndex", "adapter rebuild remainder"),
        ("KisPageStore::commit", "PageStore commit remainder"),
        ("adoptSynchronousHostWrite", "PageStore adoption remainder"),
        ("collectUnreachableHistoricalVersions", "history collection remainder"),
    ):
        if symbol in joined:
            return label
    return "other/unattributed to selected implementation paths"


def implementation_paths(path):
    roots, stack = [], []
    active = False
    for line in path.read_text().splitlines():
        if line == "Call graph:":
            active = True
            continue
        if not active:
            continue
        if line.startswith("Total number in stack"):
            break
        match = re.match(r"^([ +!:|]*)(\d+) (.+)$", line)
        if not match:
            continue
        prefix, count, name = match.groups()
        node = {"name": name, "count": int(count), "children": []}
        while stack and stack[-1][0] >= len(prefix):
            stack.pop()
        (stack[-1][1]["children"] if stack else roots).append(node)
        stack.append((len(prefix), node))
    counts = Counter()

    def visit(node, parents):
        names = parents + [node["name"]]
        own = node["count"] - sum(c["count"] for c in node["children"])
        if own < 0:
            raise ValueError("Nonconserving sampling tree")
        joined = "\n".join(names)
        if (own and "KisStressJob::run" in joined and not
                re.search(r"__psynch_\w*wait|__ulock_wait|semaphore_wait|mach_msg.*trap|__sigsuspend", joined)):
            counts[stage(joined)] += own
        for child in node["children"]:
            visit(child, names)

    for node in roots:
        if "Thread (pooled)" in node["name"]:
            visit(node, [])
    total = sum(counts.values())
    return {"file": path.name, "non_waiting_samples": total,
            "counts": dict(counts.most_common()),
            "percent": {k: 100 * v / total for k, v in counts.most_common()}}


def main():
    result = {"before": plain_runs("before-plain-*.log"),
              "d1_first": plain_runs("after-plain-*.log"),
              "d1_final": plain_runs("d1-final-plain-*.log"),
              "implementation_paths": [implementation_paths(p)
                  for p in sorted(ROOT.glob("sample-d1-*ms.txt"))],
              "qualification": "Diagnostic only; no paired upstream M/K/E qualification"}
    baseline = result["before"]["median_qt_ms"]
    for name in ("d1_first", "d1_final"):
        candidate = result[name]
        if baseline and candidate["n"] == 5:
            candidate["before_after_median_time_ratio"] = candidate["median_qt_ms"] / baseline
    analysis = json.loads((ROOT / "analysis.json").read_text())
    expected = {s["file"]: sum(s["non_waiting_structure"].values()) for s in analysis["samples"]}
    for sample in result["implementation_paths"]:
        if sample["non_waiting_samples"] != expected[sample["file"]]:
            raise ValueError("Implementation classification differs from original worker accounting")
    (ROOT / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
