#!/usr/bin/env python3
import datetime
import hashlib
import json
import os
import pathlib
import re
import subprocess
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path("/Users/apple/krita_gpu/krita")
PROTOCOL = json.loads((HERE / "repair_protocol.json").read_text())
IDENTITY_PATH = HERE / "repair-runtime-identity.json"
IDENTITY = json.loads(IDENTITY_PATH.read_text())
OUT = HERE / "repair-performance"
FIXTURE = pathlib.Path(IDENTITY["runtimes"]["candidate"]["directory"]) / "kis_tiles3_cpu_baseline_test"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_identity():
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() != PROTOCOL["source_revision"]:
        raise RuntimeError("source revision changed")
    if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True):
        raise RuntimeError("tracked source changes exist")
    if sha256(HERE / "repair_protocol.json") != IDENTITY["protocol_sha256"]:
        raise RuntimeError("selector protocol changed after runtime capture")
    if sha256(FIXTURE) != IDENTITY["runtimes"]["candidate"]["executable_sha256"]:
        raise RuntimeError("shared fixture changed")
    for variant in ["candidate", "control"]:
        directory = pathlib.Path(IDENTITY["runtimes"][variant]["directory"])
        if sha256(directory / "libkritaimage.21.0.0.dylib") != IDENTITY["runtimes"][variant]["libkritaimage_sha256"]:
            raise RuntimeError(variant + " runtime changed")


def invoke(variant, bucket, pair, loader=False):
    directory = pathlib.Path(IDENTITY["runtimes"][variant]["directory"])
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen",
           "DYLD_LIBRARY_PATH": str(directory),
           "KIS_CPU_BASELINE_LOOPS": "4",
           "KIS_CPU_BASELINE_RATE_MS": "0" if loader else str(PROTOCOL["rate_ms"]),
           "KIS_BR1_STAGE_PROFILE": "0"}
    if loader:
        env["DYLD_PRINT_LIBRARIES"] = "1"
    else:
        env.pop("DYLD_PRINT_LIBRARIES", None)
    label = "loader" if loader else f"{pair:02d}-{bucket}"
    logfile = OUT / f"{label}-{variant}.log"
    command = [str(FIXTURE), "testSharedBaseline:" + bucket]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    monotonic_start = time.monotonic_ns()
    with logfile.open("x") as stream:
        result = subprocess.run(command, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                text=True, timeout=120)
    process_wall_ns = time.monotonic_ns() - monotonic_start
    log = logfile.read_text(errors="replace")
    records = [json.loads(match) for match in re.findall(r"CPU_BASELINE (\{[^\n]+\})", log)]
    record = {
        "variant": variant, "bucket": bucket, "pair": None if loader else pair,
        "file": logfile.name, "command": command, "library": str(directory),
        "started": started, "ended": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "process_wall_ns": process_wall_ns, "returncode": result.returncode,
        "result": records[-1] if len(records) == 1 else None
    }
    manifest["runs"].append(record)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if result.returncode or len(records) != 1 or "SAFE ASSERT" in log or "FAIL!" in log or not re.search(r"Totals: 3 passed, 0 failed", log):
        raise RuntimeError(f"failed run {label}-{variant}")
    value = records[0]
    if value["fixture"] != bucket or value["mode"] != "write" or value["correctness"] != "Pass":
        raise RuntimeError("wrong fixture output")
    if loader:
        loaded = [line for line in log.splitlines() if "libkritaimage" in line]
        if len(loaded) != 1 or str(directory) not in loaded[0]:
            raise RuntimeError("wrong runtime loaded")
    elif (value["measurement"] != "completed-throughput" or
          value["wall_ns"] < PROTOCOL["rate_ms"] * 1_000_000 or
          value["completed_operations"] <= 0 or value["evidence_class"] != "E" or
          value["endpoint"] != "CpuReadable" or value["threads"] != 1 or
          value["in_flight"] != 1 or value["retained_history_roots"] != 0):
        raise RuntimeError("wrong measurement contract")
    return record


if OUT.exists():
    raise RuntimeError(f"refusing to overwrite {OUT}")
OUT.mkdir()
verify_identity()
manifest = {
    "protocol": PROTOCOL,
    "protocol_sha256": sha256(HERE / "repair_protocol.json"),
    "identity_sha256": sha256(IDENTITY_PATH),
    "started": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "runs": []
}
for variant in ["control", "candidate"]:
    invoke(variant, PROTOCOL["required_buckets"][0], -1, loader=True)
for pair in range(PROTOCOL["pairs"]):
    buckets = PROTOCOL["required_buckets"]
    ordered_buckets = buckets[pair % len(buckets):] + buckets[:pair % len(buckets)]
    variants = ["control", "candidate"] if pair % 2 == 0 else ["candidate", "control"]
    for bucket in ordered_buckets:
        for variant in variants:
            invoke(variant, bucket, pair)
    print(json.dumps({"completed_pair": pair + 1, "total_pairs": PROTOCOL["pairs"]}), flush=True)
    verify_identity()
manifest["completed"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
