#!/usr/bin/env python3
"""Verify the physical archive against its source Git revision and Markdown links."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
DESIGN = HERE.parents[1]
ROOT = DESIGN.parents[1]
LINK = re.compile(r"\]\(([^)\n]+)\)")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
LINE = re.compile(r":\d+$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def local_target(path: Path, href: str) -> Path | None:
    if href.startswith(("#", "/")) or SCHEME.match(href):
        return None
    location = href.split("#", 1)[0].split("?", 1)[0]
    if not location:
        return None
    target = (path.parent / location).resolve()
    if not target.exists() and LINE.search(location):
        target = (path.parent / LINE.sub("", location)).resolve()
    return target


def main() -> None:
    manifest = json.loads((HERE / "manifest.json").read_text())
    records = manifest["documents"]
    assert len(records) == 45
    moved = {
        (DESIGN / record["source_path"]).resolve():
        (HERE / record["archived_path"]).resolve()
        for record in records
    }
    assert len(moved) == 45

    for record in records:
        source = DESIGN / record["source_path"]
        archived = HERE / record["archived_path"]
        assert not source.exists(), source
        original = subprocess.check_output(
            ["git", "show", f"{record['source_git_revision']}:{source.relative_to(ROOT)}"],
            cwd=ROOT,
        )
        assert digest(original) == record["source_file_sha256"], source
        assert digest(original[record["notice_bytes"]:]) == record["original_sha256"], source
        actual = archived.read_bytes()
        assert digest(actual) == record["archived_sha256"], archived

        old_links = LINK.findall(original.decode("utf-8"))
        new_links = LINK.findall(actual.decode("utf-8"))
        assert len(old_links) == len(new_links), archived
        for old_href, new_href in zip(old_links, new_links):
            old_target = local_target(source, old_href)
            new_target = local_target(archived, new_href)
            if old_target is None:
                assert old_href == new_href, (archived, old_href)
            else:
                assert new_target == moved.get(old_target, old_target), (
                    archived, old_href, new_href
                )

    snapshots = json.loads((HERE / "previous-entry-snapshots.json").read_text())
    for name, record in snapshots.items():
        assert digest(record["text"].encode()) == record["sha256"], name

    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "docs/vulkan_gpu_design"], cwd=ROOT
    ).decode().split("\0")
    documents = {ROOT / name for name in tracked if name.endswith(".md")}
    documents.update(HERE / record["archived_path"] for record in records)
    checked = 0
    frozen_links = 0
    frozen_documents: set[Path] = set()
    for document in sorted(documents):
        if not document.exists():
            continue  # old tracked paths remain in the index until this move is staged
        for href in LINK.findall(document.read_text()):
            target = local_target(document, href)
            if target is not None:
                if target.exists():
                    checked += 1
                elif target in moved and document.is_relative_to(DESIGN / "evidence"):
                    assert moved[target].exists(), (document, href)
                    frozen_links += 1
                    frozen_documents.add(document)
                else:
                    raise AssertionError((document, href))

    revision = records[0]["source_git_revision"]
    for document in frozen_documents:
        original = subprocess.check_output(
            ["git", "show", f"{revision}:{document.relative_to(ROOT)}"], cwd=ROOT
        )
        assert document.read_bytes() == original, document

    print(
        f"archive: {len(records)} source/archive hash pairs, {checked} direct links, "
        f"{frozen_links} frozen-evidence links mapped"
    )


if __name__ == "__main__":
    main()
