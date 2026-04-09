#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict

def sha256_bytes(data: bytes) -> str:
return hashlib.sha256(data).hexdigest()

def canonical_json(obj: Any) -> bytes:
return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def sha256_file(path: Path) -> str:
h = hashlib.sha256()
with path.open("rb") as f:
while True:
chunk = f.read(65536)
if not chunk:
break
h.update(chunk)
return h.hexdigest()

def derive_secret_hash(evidence: Dict[str, Any]) -> str:
parts = [
evidence["protocol"],
str(evidence["stage"]),
evidence["policy_version"],
evidence["session_id"],
evidence["inputs"]["client_nonce"],
evidence["inputs"]["server_nonce"],
evidence["inputs"]["kem_ciphertext"],
]
if evidence.get("qkd_mode") == "optional" and evidence["inputs"].get("qkd_entropy"):
parts.append(evidence["inputs"]["qkd_entropy"])
return sha256_bytes("|".join(parts).encode("utf-8"))

def main() -> int:
parser = argparse.ArgumentParser()
parser.add_argument("--evidence", required=True)
parser.add_argument("--transcript", required=True)
parser.add_argument("--manifest", required=True)
parser.add_argument("--manifest-sha256", required=True)
args = parser.parse_args()

evidence_path = Path(args.evidence)
transcript_path = Path(args.transcript)
manifest_path = Path(args.manifest)
manifest_sha_path = Path(args.manifest_sha256)

evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

if evidence.get("stage") != 263:
    raise SystemExit("[FAIL] unexpected stage")
if evidence.get("protocol") != "QSP":
    raise SystemExit("[FAIL] unexpected protocol")
if evidence.get("fail_closed") is not True:
    raise SystemExit("[FAIL] fail_closed must be true")

transcript_hash = sha256_bytes(canonical_json(transcript))
if transcript_hash != evidence["result"]["transcript_sha256"]:
    raise SystemExit("[FAIL] transcript hash mismatch")
print("[OK] transcript hash matches")

derived_secret_hash = derive_secret_hash(evidence)
if derived_secret_hash != evidence["result"]["derived_secret_sha256"]:
    raise SystemExit("[FAIL] derived secret hash mismatch")
print("[OK] derived secret hash matches")

evidence_sha = sha256_file(evidence_path)
manifest_evidence_sha = manifest["artifacts"]["session_evidence"]["sha256"]
if evidence_sha != manifest_evidence_sha:
    raise SystemExit("[FAIL] evidence hash mismatch")
print("[OK] evidence hash matches manifest")

transcript_sha = sha256_file(transcript_path)
manifest_transcript_sha = manifest["artifacts"]["transcript"]["sha256"]
if transcript_sha != manifest_transcript_sha:
    raise SystemExit("[FAIL] transcript file hash mismatch")
print("[OK] transcript file hash matches manifest")

expected_manifest_sha = sha256_bytes(manifest_path.read_bytes())
recorded_line = manifest_sha_path.read_text(encoding="utf-8").strip()
recorded_sha = recorded_line.split()[0]
if expected_manifest_sha != recorded_sha:
    raise SystemExit("[FAIL] manifest sha256 mismatch")
print("[OK] manifest sha256 file matches")

print("[OK] Stage263 verification complete")
return 0

if name == "main":
raise SystemExit(main())
