#!/usr/bin/env python3
"""Reproducible standard-library analysis of macOS sample + BR1_PROFILE logs.

Sampling percentages are worker stack occupancy, NOT CPU or elapsed time.
Timed operation totals are sums across workers, NOT additive process wall time.
"""
import argparse
from collections import Counter, defaultdict
import html
import json
from pathlib import Path
import re


def sample_report(path):
    roots, stack = [], []
    in_graph = False
    for line in path.read_text().splitlines():
        if line == "Call graph:":
            in_graph = True
            continue
        if not in_graph:
            continue
        if line.startswith("Total number in stack"):
            break
        match = re.match(r"^([ +!:|]*)(\d+) (.+)$", line)
        if not match:
            continue
        prefix, count, name = match.groups()
        depth = len(prefix)
        node = {"count": int(count), "name": name, "children": []}
        while stack and stack[-1][0] >= depth:
            stack.pop()
        if stack:
            stack[-1][1]["children"].append(node)
        else:
            roots.append(node)
        stack.append((depth, node))
    occupancy, api, structure, leaf = (Counter() for _ in range(4))
    copy_paths = Counter()
    violations = []
    total = 0

    def walk(node, parents):
        names = parents + [node["name"]]
        count = node["count"]
        child_total = sum(n["count"] for n in node["children"])
        if child_total > count:
            violations.append((node["name"], count, child_total))
        own = max(0, count - child_total)
        body = next((n.split("  (in ")[0] for n in names if "KisTiledDataManager::" in n), None)
        blocked = any(re.search(r"__psynch_\w*wait|__ulock_wait|semaphore_wait|mach_msg.*trap|__sigsuspend", n) for n in names)
        job = any("KisStressJob::run" in n for n in names)
        if own:
            if not job:
                occupancy["worker outside stress body"] += own
            elif blocked and body is None:
                occupancy["test scheduling/lock wait"] += own
            elif blocked:
                occupancy["wait inside product API"] += own
            else:
                occupancy["non-waiting worker stack"] += own
                api[body or "test/Qt/other"] += own
                leaf[node["name"].split("  (in ")[0]] += own
                joined = "\n".join(names)
                if "memmove" in node["name"] or "memcpy" in node["name"]:
                    callers = [n.split("  (in ")[0] for n in names if "Kis" in n]
                    copy_paths[' -> '.join(callers[-5:])] += own
                # Exclusive path classification. First matching path owns the
                # leaf; nested categories are not added a second time.
                if "rebuildPageStoreIndex" in joined:
                    group = "index rebuild (inclusive)"
                elif "collectUnreachableHistoricalVersions" in joined or "releaseSnapshotImpl" in joined:
                    group = "history GC / snapshot release"
                elif "restoreRetainedEpochImpl" in joined:
                    group = "canonical history restore"
                elif "pruneDefaultPreparedPages" in joined:
                    group = "history default-page prune"
                elif "stageDerivedExtent" in joined:
                    group = "derive extent"
                elif "acquireRead" in joined or "refreshPageStoreData" in joined or "acquireTileRead" in joined:
                    group = "generic read / native refresh"
                elif "prepareSynchronousHostWrite" in joined or "adoptPrepared" in joined or "adoptSynchronous" in joined:
                    group = "synchronous whole-tile adoption"
                elif "ensureDefaultPageLocked" in joined:
                    group = "default-page materialization"
                elif "KisPageStore::commit" in joined:
                    group = "canonical commit"
                elif "KisPageStore::acquireWrite" in joined:
                    group = "generic mutable acquire"
                else:
                    group = "other non-waiting"
                structure[group] += own
        for child in node["children"]:
            walk(child, names)

    workers = [n for n in roots if "Thread (pooled)" in n["name"]]
    for node in workers:
        total += node["count"]
        walk(node, [])
    if violations:
        raise ValueError(f"sample tree accounting failed: {violations[:3]}")
    if sum(occupancy.values()) != total:
        raise ValueError("worker sample accounting mismatch")
    return {"file": path.name, "workers": len(workers), "worker_samples": total,
            "occupancy": dict(occupancy.most_common()),
            "non_waiting_api": dict(api.most_common()),
            "non_waiting_structure": dict(structure.most_common()),
            "copy_ancestor_paths": dict(copy_paths.most_common(12)),
            "top_non_waiting_self": dict(leaf.most_common(25))}


def timed_report(path):
    reports = []
    text = path.read_text()
    for line in text.splitlines():
        if "BR1_PROFILE {" in line:
            reports.append(json.loads(line[line.index('{'):]))
    if not reports:
        return None
    counters = None
    for line in text.splitlines():
        if "BR1_COUNTERS {" in line:
            counters = json.loads(line[line.index('{'):])
    tables = {}
    for kind in ("operations", "phases"):
        rows = defaultdict(Counter)
        for report in reports:
            for row in report[kind]:
                name = row["name"]
                if name in ("history_7", "history_8"):
                    name = "history"
                elif name in ("tile_locks_1", "tile_locks_2"):
                    name = "tile_locks"
                for field in ("count", "wall_ms", "cpu_ms", "wait_ms"):
                    rows[name][field] += row[field]
        tables[kind] = dict(sorted(rows.items(), key=lambda x: -x[1]["wall_ms"]))
    match = re.search(r"Totals: .*?, (\d+)ms", text)
    if not match or "0 failed" not in text:
        raise ValueError(f"incomplete or failed diagnostic run: {path}")
    if sum(row["count"] for row in tables["operations"].values()) != 80000:
        raise ValueError(f"expected eight 10000-cycle worker streams: {path}")
    return {"file": path.name, "workers": len(reports),
            "qt_elapsed_ms": int(match[1]) if match else None,
            "counters": counters,
            "cpu_clock_available": all(r["cpu_clock_available"] for r in reports),
            **tables}


def chart(path, title, subtitle, rows, unit, width=1150):
    height = 115 + len(rows) * 43
    maximum = max((v for _, v, _ in rows), default=1) or 1
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="#f6f8fb"/>',
             '<g font-family="Arial, sans-serif" fill="#152238">',
             f'<text x="24" y="32" font-size="22" font-weight="bold">{html.escape(title)}</text>',
             f'<text x="24" y="58" font-size="13">{html.escape(subtitle)}</text>']
    for index, (name, value, cpu) in enumerate(rows):
        y = 82 + index * 43
        bar = value / maximum * 600
        parts.extend([f'<text x="24" y="{y+17}" font-size="14">{html.escape(name)}</text>',
                      f'<rect x="390" y="{y}" width="{bar:.2f}" height="24" rx="3" fill="#c2d7ed"/>'])
        if cpu is not None:
            parts.append(f'<rect x="390" y="{y}" width="{cpu/maximum*600:.2f}" height="24" rx="3" fill="#2474ac"/>')
        parts.append(f'<text x="{max(998, 398+bar):.2f}" y="{y+17}" font-size="13">{value:.2f} {unit}</text>')
    parts.append('</g></svg>')
    path.write_text('\n'.join(parts))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--timed-run", help="Explicit timed log for phase charts; never mix different revisions")
    args = parser.parse_args()
    directory = args.directory
    samples = [sample_report(p) for p in sorted(directory.glob("sample-*.txt"))]
    timings = [r for p in sorted(directory.glob("timed-*.log")) if (r := timed_report(p))]
    result = {"samples": samples, "timings": timings}
    (directory / "analysis.json").write_text(json.dumps(result, indent=2) + '\n')
    for sample in samples:
        stem = Path(sample["file"]).stem
        count = sample["worker_samples"]
        chart(directory / f"{stem}-occupancy.svg", "Stress worker stack occupancy",
              "Blocked and runnable stacks are both sampled; percentages are NOT CPU time.",
              [(k, v / count * 100, None) for k, v in sample["occupancy"].items()], "%")
        groups = sample["non_waiting_structure"]
        total = sum(groups.values()) or 1
        chart(directory / f"{stem}-structure.svg", "Non-waiting worker stack structure",
              "Exclusive leaf attribution by ancestor path; no double counting. Statistical evidence, not exact durations.",
              [(k, v / total * 100, None) for k, v in groups.items()], "%")
    if timings:
        # Choose the eight-thread run with counters, never an average over
        # unlike worker counts or cold/warm configurations.
        if args.timed_run:
            chosen = next((r for r in timings if r["file"] == args.timed_run), None)
            if chosen is None:
                raise ValueError(f"Selected timed run is missing: {args.timed_run}")
        else:
            chosen = next((r for r in timings if r["file"] == "timed-03-counters.log"), timings[0])
        chart(directory / "operations.svg", "Operation body wall time and thread CPU time",
              chosen["file"] + "; sum across workers. Light=body wall, dark=thread CPU. Excludes outer test-lock waiting.",
              [(k, v["wall_ms"] / 1000, v["cpu_ms"] / 1000) for k, v in chosen["operations"].items()], "s")
        chart(directory / "history.svg", "History operation phase costs",
              chosen["file"] + "; history phases only. Light=body wall, dark=thread CPU. API costs include nested work.",
              [(k, v["wall_ms"] / 1000, v["cpu_ms"] / 1000) for k, v in chosen["phases"].items()
               if k not in ("read_bytes", "write_identical_bytes")], "s")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
