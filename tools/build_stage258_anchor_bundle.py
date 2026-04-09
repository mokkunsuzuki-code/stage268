#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
from pathlib import Path
from typing import Any

CHAIN_DIR = Path("out/third_party_chain")
ANCHOR_DIR = Path("out/anchors")
CHAIN_INDEX_PATH = CHAIN_DIR / "chain_index.json"
BUNDLE_PATH = ANCHOR_DIR / "stage258_third_party_chain_bundle.tar.gz"
MANIFEST_PATH = ANCHOR_DIR / "stage258_chain_anchor_manifest.json"
MANIFEST_SHA256_PATH = ANCHOR_DIR / "stage258_chain_anchor_manifest.sha256"
RECEIPT_TEMPLATE_PATH = ANCHOR_DIR / "stage258_chain_anchor_receipt.json"

def canonical_json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def git_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True).strip()
    except Exception:
        return None

def build_bundle() -> None:
    if not CHAIN_INDEX_PATH.exists():
        raise FileNotFoundError(f"missing chain index: {CHAIN_INDEX_PATH}")

    ANCHOR_DIR.mkdir(parents=True, exist_ok=True)

    with tarfile.open(BUNDLE_PATH, "w:gz") as tar:
        tar.add(CHAIN_DIR, arcname="third_party_chain")

    bundle_sha256 = sha256_bytes(BUNDLE_PATH.read_bytes())
    chain_index = load_json(CHAIN_INDEX_PATH)
    chain_index_sha256 = sha256_bytes(CHAIN_INDEX_PATH.read_bytes())

    manifest = {
        "version": 1,
        "stage": "stage258",
        "anchor_type": "external_release_ready_anchor",
        "generated_at": utc_now_iso(),
        "repository": git_output(["git", "config", "--get", "remote.origin.url"]),
        "git_commit": git_output(["git", "rev-parse", "HEAD"]),
        "git_branch": git_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "chain_summary": {
            "record_count": chain_index.get("record_count"),
            "latest_record_id": chain_index.get("latest_record_id"),
            "latest_record_sha256": chain_index.get("latest_record_sha256"),
            "chain_index_sha256": chain_index_sha256,
        },
        "artifacts": {
            "bundle_path": str(BUNDLE_PATH),
            "bundle_sha256": bundle_sha256,
            "chain_index_path": str(CHAIN_INDEX_PATH),
        },
    }

    save_json(MANIFEST_PATH, manifest)
    manifest_sha256 = sha256_bytes(MANIFEST_PATH.read_bytes())
    MANIFEST_SHA256_PATH.write_text(
        f"{manifest_sha256}  {MANIFEST_PATH.name}\n",
        encoding="utf-8",
    )

    receipt_template = {
        "version": 1,
        "stage": "stage258",
        "description": "Fill this after publishing the anchor bundle to an external location such as GitHub Release.",
        "release_tag": None,
        "release_url": None,
        "published_bundle_sha256": bundle_sha256,
        "published_manifest_sha256": manifest_sha256,
        "published_at": None,
    }
    save_json(RECEIPT_TEMPLATE_PATH, receipt_template)

    print("[OK] Stage258 anchor bundle created")
    print(f"[OK] bundle: {BUNDLE_PATH}")
    print(f"[OK] bundle_sha256: {bundle_sha256}")
    print(f"[OK] manifest: {MANIFEST_PATH}")
    print(f"[OK] manifest_sha256: {manifest_sha256}")

if __name__ == "__main__":
    build_bundle()
