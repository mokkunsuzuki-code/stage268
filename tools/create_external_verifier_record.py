#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

CHAIN_DIR = Path("out/verifier_chain")
RECORDS_DIR = CHAIN_DIR / "records"
INDEX_PATH = CHAIN_DIR / "verifier_chain_index.json"

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

def ensure_index() -> dict[str, Any]:
    if INDEX_PATH.exists():
        return load_json(INDEX_PATH)

    index = {
        "version": 1,
        "chain_name": "external_verifier_proof_chain",
        "created_at": utc_now_iso(),
        "record_count": 0,
        "latest_record_id": None,
        "latest_record_sha256": None,
        "records": [],
    }
    save_json(INDEX_PATH, index)
    return index

def next_record_id(index: dict[str, Any]) -> str:
    return f"verifier_record_{index['record_count'] + 1:04d}"

def main() -> None:
    parser = argparse.ArgumentParser(description="Append an external verifier proof record.")
    parser.add_argument("--verifier-id", required=True)
    parser.add_argument("--verifier-type", required=True)
    parser.add_argument("--target-release-tag", required=True)
    parser.add_argument("--target-release-url", required=True)
    parser.add_argument("--target-bundle-sha256", required=True)
    parser.add_argument("--target-manifest-sha256", required=True)
    parser.add_argument("--verification-result", required=True)
    parser.add_argument("--verification-method", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--evidence-path", action="append", default=[])
    parser.add_argument("--verified-at", default=None)
    args = parser.parse_args()

    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    index = ensure_index()

    record_id = next_record_id(index)
    prev_record_id = index["latest_record_id"]
    prev_record_sha256 = index["latest_record_sha256"]

    payload = {
        "version": 1,
        "record_id": record_id,
        "verified_at": args.verified_at or utc_now_iso(),
        "verifier": {
            "id": args.verifier_id,
            "type": args.verifier_type,
        },
        "target": {
            "release_tag": args.target_release_tag,
            "release_url": args.target_release_url,
            "bundle_sha256": args.target_bundle_sha256,
            "manifest_sha256": args.target_manifest_sha256,
        },
        "verification": {
            "result": args.verification_result,
            "method": args.verification_method,
            "notes": args.notes,
            "evidence_paths": args.evidence_path,
        },
    }

    payload_sha256 = sha256_bytes(canonical_json_bytes(payload))

    record = {
        "version": 1,
        "record_id": record_id,
        "prev_record_id": prev_record_id,
        "prev_record_sha256": prev_record_sha256,
        "payload_sha256": payload_sha256,
        "payload": payload,
    }

    record_bytes = canonical_json_bytes(record)
    record_sha256 = sha256_bytes(record_bytes)

    record_path = RECORDS_DIR / f"{record_id}.json"
    record_path.write_bytes(record_bytes)

    index["record_count"] += 1
    index["latest_record_id"] = record_id
    index["latest_record_sha256"] = record_sha256
    index["records"].append(
        {
            "record_id": record_id,
            "path": str(record_path),
            "record_sha256": record_sha256,
            "payload_sha256": payload_sha256,
            "verifier_id": args.verifier_id,
            "verification_result": args.verification_result,
            "verified_at": payload["verified_at"],
        }
    )

    save_json(INDEX_PATH, index)

    print("[OK] external verifier record appended")
    print(f"[OK] record_id: {record_id}")
    print(f"[OK] record_sha256: {record_sha256}")
    if prev_record_id:
        print(f"[OK] linked_to: {prev_record_id}")
    else:
        print("[OK] linked_to: genesis")
    print(f"[OK] total_records: {index['record_count']}")

if __name__ == "__main__":
    main()
