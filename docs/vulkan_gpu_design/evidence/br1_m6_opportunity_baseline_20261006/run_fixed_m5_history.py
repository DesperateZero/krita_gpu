"""Pre-registered bounded public history control against fixed M5."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIXTURE = HERE.parent / "br1_cp3_handoff_storage_reuse_20261006"
parser = argparse.ArgumentParser()
parser.add_argument("--round", default="fixed-m5-history")
OUT = HERE / parser.parse_args().round
OUT.mkdir()
builds = {"current": ROOT / "krita/_build-br0-cpu", "m5": ROOT / "build/br1-fixed-m5-20261005/build"}
sources = {"current": ROOT / "krita", "m5": ROOT / "build/br1-fixed-m5-20261005/source"}
protocol = dict(scope="Fixed5173 same-dependency public full-payload/history control; same external source on each tree",
    buckets=[[a, n, k] for a in ["arm64", "x86_64"] for n,k in [[64,1],[1024,16]]], H_transactions=4, B=4,
    pairs=40, rate_ms=250, completed_rate_check_interval=64, loops=4,
    endpoint="Public full-payload write/commit, all-page sentinel reads, bounded four-memento retention/purge; setup and final undo/redo/close outside",
    independent_unit="process pair; adjacent even/odd pairs form20 predeclared order-balanced blocks",
    order="rotate four buckets and alternate m5/current order per pair; sequential processes; no concurrent builds or benchmarks",
    statistic="median block geometric mean of two completed-work throughput ratios; 50000 bootstrap blocks seed260926",
    confidence="one-sided98.75% per bucket, family at least95% across four buckets", minimum_throughput_ratio=.98,
    stopping="exactly40 pairs; stop only for correctness/process/identity failure, preserve all failures; no trimming or extension",
    limits="Four public undo transactions, not an assertion of four native root handles; not handoff latency/upstream/stroke E/tails or full M6")
(OUT / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
paths = [Path(__file__), OUT / "protocol.json"]
for variant, build in builds.items():
    paths += list((build / "bin").glob("*.dylib")) + [build / "CMakeCache.txt"]
    paths += [FIXTURE / f"control-history-{variant}-{arch}/probe" for arch in ["arm64", "x86_64"]]
    names = subprocess.check_output(["git", "ls-files", "libs/image"], cwd=sources[variant], text=True).splitlines()
    paths += [sources[variant] / name for name in names if Path(name).suffix in [".cpp", ".cc", ".h"]]
paths += [ROOT / "krita/_install/lib" / (q + ".framework/Versions/A/" + q) for q in ["QtCore", "QtTest", "QtGui", "QtWidgets"]]
paths += [FIXTURE / "fresh-history-throughput.cpp", FIXTURE / "build_control_probe.py"]
identity = {str(path): digest(path) for path in paths}
(OUT / "identity-before.json").write_text(json.dumps(identity, indent=2) + "\n")
runs = []
for pair in range(40):
    buckets = protocol["buckets"]
    for arch, n, k in buckets[pair % 4:] + buckets[:pair % 4]:
        for variant in (["m5", "current"] if pair % 2 == 0 else ["current", "m5"]):
            build = builds[variant]
            tag = f"write-n{n}-k{k}-b4"
            label = f"{pair:02d}-{arch}-k{k}-{variant}"
            command = ["arch", "-"+arch, "/usr/bin/env", "DYLD_LIBRARY_PATH="+str(build / "bin"),
                "DYLD_PRINT_LIBRARIES=1", str(FIXTURE / f"control-history-{variant}-{arch}/probe"), str(k), "4", "250"]
            env = {**os.environ, "QT_QPA_PLATFORM":"offscreen", "KIS_CPU_BASELINE_LOOPS":"4", "KIS_CPU_BASELINE_RATE_MS":"250",
                "KIS_BR1_PROFILE":"0", "KIS_BR1_STAGE_PROFILE":"0", "KIS_TEST_PREFIX_PATH":str(ROOT / "krita/_install"),
                "KIS_TEST_PLUGIN_PATH":str(build / "bin")}
            start = time.monotonic()
            with (OUT / (label+".log")).open("x") as stream:
                p = subprocess.Popen(command, cwd=sources[variant], env=env, stdout=stream, stderr=subprocess.STDOUT)
                try:
                    code, timeout = p.wait(timeout=120), False
                except subprocess.TimeoutExpired:
                    p.kill()
                    code, timeout = p.wait(timeout=5), True
            raw = (OUT / (label+".log")).read_text()
            data = [json.loads(line.removeprefix("CONTROL ")) for line in raw.splitlines() if line.startswith("CONTROL ")]
            row = dict(pair=pair, arch=arch, N=n, K=k, variant=variant, command=command, pid=p.pid,
                exit_code=code, reaped=True, timed_out=timeout, seconds=time.monotonic()-start, data=data,
                image_loaded=str(build / "bin/libkritaimage.21.0.0.dylib") in raw,
                failures=re.findall(r"^.*(?:FAIL!|FATAL|SAFE ASSERT|ASSERT failure).*$",raw,re.M))
            runs.append(row)
            (OUT / "runs.json").write_text(json.dumps(runs, indent=2)+"\n")
            if code or timeout or row["failures"] or not row["image_loaded"] or len(data)!=1 or "all_checks_passed=1" not in raw:
                raise RuntimeError(row)
            value = data[0]
            assert value["N"]==n and value["K"]==k and value["H_transactions"]==4 and value["undo_redo_checked"]
            assert value["completed_operations"]>=64 and value["wall_ns"]>=250000000
    print(json.dumps(dict(completed_pair=pair+1)), flush=True)
for name, expected in identity.items():
    assert digest(Path(name))==expected, name
(OUT / "identity-final.json").write_text(json.dumps(dict(hashes=identity, inputs_verified=True),indent=2)+"\n")
