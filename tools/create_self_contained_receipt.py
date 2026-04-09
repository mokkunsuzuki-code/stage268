import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization


def canonical_json_bytes(obj: dict) -> bytes:
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def load_private_key(path: Path):
    return serialization.load_pem_private_key(path.read_bytes(), password=None)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    private_key_path = Path("keys/ed25519_private.pem")
    public_key_path = Path("keys/ed25519_public.pem")

    if not private_key_path.exists():
        raise FileNotFoundError("Missing private key: keys/ed25519_private.pem")
    if not public_key_path.exists():
        raise FileNotFoundError("Missing public key: keys/ed25519_public.pem")

    private_key = load_private_key(private_key_path)
    public_pem_bytes = public_key_path.read_bytes()

    receipt = {
        "receipt_version": 2,
        "review_id": "review-002",
        "review_type": "self_contained_external_feedback_response",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "signer_identity": "Motohiro Suzuki",
        "signature_algorithm": "Ed25519",
        "verification_mode": "self_contained",
        "verification_material": {
            "embedded_public_key_pem": public_pem_bytes.decode("utf-8"),
            "embedded_public_key_sha256": sha256_hex(public_pem_bytes),
            "verification_url": None
        },
        "key_lifecycle": {
            "key_id": "key-002",
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2027-01-01T00:00:00Z",
            "revoked": False,
            "previous_key_id": "key-001",
            "rotation_reason": "self-contained verification transition"
        },
        "content": {
            "result": "accepted_feedback",
            "summary": "Stage262 introduces self-contained reviewer receipt verification.",
            "comment": "Verification can be performed from the receipt alone without requiring a separate public key file."
        }
    }

    signed_payload = canonical_json_bytes(receipt)
    signature = private_key.sign(signed_payload)

    receipt["signature"] = {
        "encoding": "base64",
        "value": base64.b64encode(signature).decode("ascii")
    }

    out_dir = Path("out/receipts")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "review_receipt_self_contained.json"
    out_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"[OK] self-contained receipt created: {out_path}")


if __name__ == "__main__":
    main()
