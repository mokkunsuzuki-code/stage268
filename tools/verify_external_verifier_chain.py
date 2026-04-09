#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

CHAIN_DIR = Path("out/verifier_chain")
INDEX_PATH = CHAIN_DIR / "verifier_chain_index.json"
RECEIPT_PATH = Path("out/anchors/stage258_chain_anchor_receipt.json")

def canonical_json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)

def main() -> None:
    if not INDEX_PATH.exists():
        fail(f"missing index: {INDEX_PATH}")
    if not RECEIPT_PATH.exists():
        fail(f"missing receipt: {RECEIPT_PATH}")

    index = load_json(INDEX_PATH)
    receipt = load_json(RECEIPT_PATH)
    records = index.get("records", [])

    if index.get("record_count") != len(records):
        fail("record_count mismatch")

    expected_release_tag = receipt.get("release_tag")
    expected_release_url = receipt.get("release_url")
    expected_bundle_sha256 = receipt.get("published_bundle_sha256")
    expected_manifest_sha256 = receipt.get("published_manifest_sha256")

    prev_record_id = None
    prev_record_sha256 = None

    for i, entry in enumerate(records, start=1):
        expected_record_id = f"verifier_record_{i:04d}"
        record_path = Path(entry["path"])
        if not record_path.exists():
            fail(f"missing record file: {record_path}")

        record = load_json(record_path)
        if record["record_id"] != expected_record_id:
            fail(f"unexpected record order: got {record['record_id']}, expected {expected_record_id}")
        if record["prev_record_id"] != prev_record_id:
            fail(f"prev_record_id mismatch at {record['record_id']}")
        if record["prev_record_sha256"] != prev_record_sha256:
            fail(f"prev_record_sha256 mismatch at {record['record_id']}")

        payload = record["payload"]
        target = payload["target"]

        if target["release_tag"] != expected_release_tag:
            fail(f"release_tag mismatch at {record['record_id']}")
        if target["release_url"] != expected_release_url:
            fail(f"release_url mismatch at {record['record_id']}")
        if target["bundle_sha256"] != expected_bundle_sha256:
            fail(f"bundle_sha256 mismatch at {record['record_id']}")
        if target["manifest_sha256"] != expected_manifest_sha256:
            fail(f"manifest_sha256 mismatch at {record['record_id']}")

        payload_sha256 = sha256_bytes(canonical_json_bytes(payload))
        if record["payload_sha256"] != payload_sha256:
            fail(f"payload_sha256 mismatch at {record['record_id']}")

        record_sha256 = sha256_bytes(canonical_json_bytes(record))
        if entry["record_sha256"] != record_sha256:
            fail(f"record_sha256 mismatch at {record['record_id']}")

        prev_record_id = record["record_id"]
        prev_record_sha256 = record_sha256

    if records:
        if index["latest_record_id"] != prev_record_id:
            fail("latest_record_id mismatch")
        if index["latest_record_sha256"] != prev_record_sha256:
            fail("latest_record_sha256 mismatch")

    print("[OK] external verifier proof chain verified")
    print(f"[OK] record_count: {len(records)}")
    if records:
        print(f"[OK] latest_record_id: {index['latest_record_id']}")
        print(f"[OK] release_tag: {expected_release_tag}")

if __name__ == "__main__":
    main()
