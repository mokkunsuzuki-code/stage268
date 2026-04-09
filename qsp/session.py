import hashlib
import json
from typing import Any, Dict, List

def _sha256_bytes(data: bytes) -> str:
return hashlib.sha256(data).hexdigest()

def _canonical_json(obj: Any) -> bytes:
return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def _build_transcript(config: Dict[str, Any]) -> List[Dict[str, Any]]:
return [
{
"seq": 1,
"type": "CLIENT_HELLO",
"session_id": config["session_id"],
"suite": config["suite"],
"client_nonce": config["client_nonce"],
},
{
"seq": 2,
"type": "SERVER_HELLO",
"session_id": config["session_id"],
"suite": config["suite"],
"server_nonce": config["server_nonce"],
},
{
"seq": 3,
"type": "KEM_CIPHERTEXT",
"session_id": config["session_id"],
"kem_ciphertext": config["kem_ciphertext"],
"qkd_mode": config["qkd_mode"],
},
{
"seq": 4,
"type": "FINISH",
"session_id": config["session_id"],
"fail_closed": config["fail_closed"],
},
]

def _derive_secret_material(config: Dict[str, Any]) -> str:
parts = [
config["protocol"],
str(config["stage"]),
config["policy_version"],
config["session_id"],
config["client_nonce"],
config["server_nonce"],
config["kem_ciphertext"],
]

if config.get("qkd_mode") == "optional" and config.get("qkd_entropy"):
    parts.append(config["qkd_entropy"])

return "|".join(parts)

def run_session(config: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
transcript = _build_transcript(config)
transcript_hash = _sha256_bytes(_canonical_json(transcript))

derived_secret_material = _derive_secret_material(config)
derived_secret_hash = _sha256_bytes(derived_secret_material.encode("utf-8"))

if not config.get("fail_closed", False):
    raise ValueError("Stage263 requires fail_closed=true")

if not transcript:
    raise ValueError("Transcript must not be empty")

evidence = {
    "protocol": config["protocol"],
    "stage": config["stage"],
    "policy_version": config["policy_version"],
    "suite": config["suite"],
    "session_id": config["session_id"],
    "qkd_mode": config["qkd_mode"],
    "fail_closed": config["fail_closed"],
    "inputs": {
        "client_nonce": config["client_nonce"],
        "server_nonce": config["server_nonce"],
        "kem_ciphertext": config["kem_ciphertext"],
        "qkd_entropy": config.get("qkd_entropy", ""),
    },
    "result": {
        "status": "ok",
        "transcript_sha256": transcript_hash,
        "derived_secret_sha256": derived_secret_hash,
        "message_count": len(transcript),
    },
    "metadata": {
        "repository": metadata.get("repository", ""),
        "commit_sha": metadata.get("commit_sha", ""),
        "run_id": metadata.get("run_id", ""),
        "generated_by": "tools/run_stage263_qsp.py",
    },
}

return {
    "transcript": transcript,
    "evidence": evidence,
}

