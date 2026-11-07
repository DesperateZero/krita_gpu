#!/usr/bin/env python3
import datetime
import hashlib
import json
import os
import pathlib
import platform
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path("/Users/apple/krita_gpu/krita")
BUILD = ROOT / "_build-br0-cpu"
BIN = BUILD / "bin"
NINJA = pathlib.Path("/Users/apple/krita_gpu/.venv/bin/ninja")
PROTOCOL = json.loads((HERE / "protocol-final.json").read_text())
TESTS = PROTOCOL["page_store_tests"] + PROTOCOL["business_tests"]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command, *, cwd=ROOT, env=None, log=None, timeout=900):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, timeout=timeout)
    ended = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if log:
        pathlib.Path(log).write_text(result.stdout)
    return {
        "command": command,
        "started": started,
        "ended": ended,
        "returncode": result.returncode,
        "output": result.stdout,
    }


def require_clean_source():
    revision = run(["git", "rev-parse", "HEAD"])["output"].strip()
    if revision != PROTOCOL["source_revision"]:
        raise RuntimeError(f"source revision {revision} does not match protocol")
    tracked = run(["git", "status", "--porcelain", "--untracked-files=no"])["output"]
    if tracked:
        raise RuntimeError("tracked source changes exist before evidence run:\n" + tracked)


def main():
    output = HERE / "correctness-final"
    if output.exists():
        raise RuntimeError(f"refusing to overwrite {output}")
    output.mkdir()
    require_clean_source()

    build = run([str(NINJA), "-C", str(BUILD), "-j", "6", *TESTS], log=output / "build.log", timeout=1800)
    if build["returncode"]:
        raise RuntimeError("build failed; see correctness-final/build.log")

    identity = {
        "captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_revision": PROTOCOL["source_revision"],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": sys.version,
        "files": {},
    }
    for path in [BUILD / "CMakeCache.txt", BUILD / "compile_commands.json",
                 ROOT / "build-tools/ci-scripts/pagestore-audit/baseline-source.json",
                 ROOT / "build-tools/ci-scripts/pagestore-audit/reverse-callgraph.json", BIN / "libkritaimage.21.0.0.dylib"] + [BIN / name for name in TESTS]:
        identity["files"][str(path)] = {"size": path.stat().st_size, "sha256": sha256(path)}
    (output / "identity.json").write_text(json.dumps(identity, indent=2) + "\n")

    architecture = run([
        "python3", "build-tools/ci-scripts/check-pagestore-architecture.py",
        "--build-dir", "_build-br0-cpu"
    ], log=output / "architecture.log")
    self_tests = run([
        "python3", "-m", "unittest", "discover", "-s",
        "build-tools/ci-scripts/tests", "-p", "test_pagestore_reachability.py"
    ], log=output / "reachability-self-tests.log")
    if architecture["returncode"] or self_tests["returncode"]:
        raise RuntimeError("architecture validation failed")

    base_env = os.environ.copy()
    base_env.update(PROTOCOL["environment"])
    manifest = []
    for architecture_name in PROTOCOL["architectures"]:
        arch_dir = output / architecture_name
        arch_dir.mkdir()
        for name in TESTS:
            command = ["arch", "-" + architecture_name, str(BIN / name)]
            result = run(command, env=base_env, log=arch_dir / (name + ".log"), timeout=1200)
            totals = re.findall(r"Totals: (\d+) passed, (\d+) failed, (\d+) skipped", result["output"])
            record = {
                "architecture": architecture_name,
                "test": name,
                "command": command,
                "started": result["started"],
                "ended": result["ended"],
                "returncode": result["returncode"],
                "totals": totals[-1] if totals else None,
                "log": str((arch_dir / (name + ".log")).relative_to(HERE)),
            }
            manifest.append(record)
            (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
            print(json.dumps(record), flush=True)
            if (result["returncode"] != 0 or not totals or totals[-1][1] != "0"
                    or "SAFE ASSERT" in result["output"] or "FAIL!" in result["output"]):
                raise RuntimeError(f"{architecture_name} {name} failed")

    dry_run = run([str(NINJA), "-C", str(BUILD), "-n", *TESTS],
                  log=output / "final-build-dry-run.log")
    if dry_run["returncode"] or "no work to do" not in dry_run["output"]:
        raise RuntimeError("final build is not source-current")

    require_clean_source()
    vulkan = PROTOCOL["vulkan_compatibility"]
    vkbuild = pathlib.Path(vulkan["build_directory"])
    vkexe = vkbuild / "bin" / vulkan["target"]
    vkresult = run([str(NINJA), "-C", str(vkbuild), "-j", "6", vulkan["target"]], log=output / "vulkan-build.log", timeout=1800)
    if vkresult["returncode"]: raise RuntimeError("Vulkan compatibility build failed")
    vkmanifest = []
    for architecture_name in vulkan["architectures"]:
        command = ["arch", "-" + architecture_name, str(vkexe)]
        result = run(command, env=base_env, log=output / ("vulkan-" + architecture_name + ".log"))
        totals = re.findall(r"Totals: (\d+) passed, (\d+) failed, (\d+) skipped", result["output"])
        vkmanifest.append({"command": command, "returncode": result["returncode"], "totals": totals, "binary_sha256": sha256(vkexe)})
        (output / "vulkan-manifest.json").write_text(json.dumps(vkmanifest, indent=2) + "\n")
        if result["returncode"] or not totals or totals[-1][1] != "0": raise RuntimeError("Vulkan contracts failed")
    print("same-source CPU and Vulkan validation complete", flush=True)


if __name__ == "__main__":
    main()
