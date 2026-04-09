#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

CHAIN_INDEX_PATH = Path("out/third_party_chain/chain_index.json")
BUNDLE_PATH = Path("out/anchors/stage258_third_party_chain_bundle.tar.gz")
MANIFEST_PATH = Path("out/anchors/stage258_chain_anchor_manifest.json")
MANIFEST_SHA256_PATH = Path("out/anchors/stage258_chain_anchor_manifest.sha256")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)

def main() -> None:
    if not CHAIN_INDEX_PATH.exists():
        fail(f"missing {CHAIN_INDEX_PATH}")
    if not BUNDLE_PATH.exists():
        fail(f"missing {BUNDLE_PATH}")
    if not MANIFEST_PATH.exists():
        fail(f"missing {MANIFEST_PATH}")
    if not MANIFEST_SHA256_PATH.exists():
        fail(f"missing {MANIFEST_SHA256_PATH}")

    chain_index = load_json(CHAIN_INDEX_PATH)
    manifest = load_json(MANIFEST_PATH)

    actual_bundle_sha256 = sha256_bytes(BUNDLE_PATH.read_bytes())
    actual_manifest_sha256 = sha256_bytes(MANIFEST_PATH.read_bytes())
    actual_chain_index_sha256 = sha256_bytes(CHAIN_INDEX_PATH.read_bytes())

    manifest_sha_line = MANIFEST_SHA256_PATH.read_text(encoding="utf-8").strip()
    expected_manifest_sha256 = manifest_sha_line.split()[0]

    if expected_manifest_sha256 != actual_manifest_sha256:
        fail("manifest sha256 mismatch")

    summary = manifest.get("chain_summary", {})
    artifacts = manifest.get("artifacts", {})

    if summary.get("record_count") != chain_index.get("record_count"):
        fail("record_count mismatch")
    if summary.get("latest_record_id") != chain_index.get("latest_record_id"):
        fail("latest_record_id mismatch")
    if summary.get("latest_record_sha256") != chain_index.get("latest_record_sha256"):
        fail("latest_record_sha256 mismatch")
    if summary.get("chain_index_sha256") != actual_chain_index_sha256:
        fail("chain_index_sha256 mismatch")
    if artifacts.get("bundle_sha256") != actual_bundle_sha256:
        fail("bundle_sha256 mismatch")

    print("[OK] Stage258 anchor verified")
    print(f"[OK] record_count: {chain_index.get('record_count')}")
    print(f"[OK] latest_record_id: {chain_index.get('latest_record_id')}")
    print(f"[OK] bundle_sha256: {actual_bundle_sha256}")
    print(f"[OK] manifest_sha256: {actual_manifest_sha256}")

if __name__ == "__main__":
    main()
