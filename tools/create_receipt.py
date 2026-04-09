import json
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization


def load_private_key(path: Path):
    return serialization.load_pem_private_key(path.read_bytes(), password=None)


def canonical_json_bytes(obj: dict) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def main() -> None:
    private_key_path = Path("keys/ed25519_private.pem")
    if not private_key_path.exists():
        raise FileNotFoundError("Missing private key: keys/ed25519_private.pem")

    private_key = load_private_key(private_key_path)

    receipt = {
        "receipt_version": 1,
        "review_id": "review-001",
        "review_type": "external_feedback_response",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "signer_identity": "Motohiro Suzuki",
        "signature_algorithm": "Ed25519",
        "verification_method": "local_public_key",
        "verification_material": {
            "public_key_path": "keys/ed25519_public.pem"
        },
        "key_lifecycle": {
            "key_id": "key-001",
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2027-01-01T00:00:00Z",
            "revoked": False,
            "previous_key_id": None,
            "rotation_reason": None
        },
        "content": {
            "result": "accepted_feedback",
            "summary": "Stage261 introduces lifecycle-aware reviewer receipts.",
            "comment": "This receipt demonstrates algorithm agility readiness and key lifecycle metadata."
        }
    }

    data = canonical_json_bytes(receipt)
    signature = private_key.sign(data).hex()

    signed_receipt = dict(receipt)
    signed_receipt["signature"] = signature

    out_dir = Path("out/receipts")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "review_receipt.json"
    out_path.write_text(json.dumps(signed_receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] receipt created: {out_path}")


if __name__ == "__main__":
    main()
