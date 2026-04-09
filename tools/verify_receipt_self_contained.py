import base64
import hashlib
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization


REQUIRED_TOP_LEVEL_FIELDS = {
    "receipt_version",
    "review_id",
    "review_type",
    "created_at",
    "signer_identity",
    "signature_algorithm",
    "verification_mode",
    "verification_material",
    "key_lifecycle",
    "content",
    "signature",
}


def canonical_json_bytes(obj: dict) -> bytes:
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 tools/verify_receipt_self_contained.py <receipt.json>")
        sys.exit(1)

    receipt_path = Path(sys.argv[1])
    if not receipt_path.exists():
        print(f"[FAIL] receipt not found: {receipt_path}")
        sys.exit(1)

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

    missing = REQUIRED_TOP_LEVEL_FIELDS - set(receipt.keys())
    if missing:
        print(f"[FAIL] missing required fields: {sorted(missing)}")
        sys.exit(1)

    if receipt.get("signature_algorithm") != "Ed25519":
        print(f"[FAIL] unsupported signature_algorithm: {receipt.get('signature_algorithm')}")
        sys.exit(1)

    if receipt.get("verification_mode") != "self_contained":
        print(f"[FAIL] unsupported verification_mode: {receipt.get('verification_mode')}")
        sys.exit(1)

    verification_material = receipt.get("verification_material", {})
    embedded_public_key_pem = verification_material.get("embedded_public_key_pem")
    embedded_public_key_sha256 = verification_material.get("embedded_public_key_sha256")

    if not embedded_public_key_pem:
        print("[FAIL] missing embedded public key")
        sys.exit(1)

    public_key_bytes = embedded_public_key_pem.encode("utf-8")
    computed_fingerprint = sha256_hex(public_key_bytes)

    if embedded_public_key_sha256 != computed_fingerprint:
        print("[FAIL] embedded public key fingerprint mismatch")
        sys.exit(1)

    public_key = serialization.load_pem_public_key(public_key_bytes)

    signature_obj = receipt.get("signature", {})
    if signature_obj.get("encoding") != "base64":
        print("[FAIL] unsupported signature encoding")
        sys.exit(1)

    signature_b64 = signature_obj.get("value")
    if not signature_b64:
        print("[FAIL] missing signature value")
        sys.exit(1)

    unsigned_receipt = dict(receipt)
    signature = base64.b64decode(unsigned_receipt.pop("signature")["value"])

    # reconstruct exact signature object removal
    unsigned_receipt["signature"] = receipt["signature"]
    unsigned_receipt.pop("signature")

    try:
        public_key.verify(signature, canonical_json_bytes(unsigned_receipt))
    except Exception as exc:
        print(f"[FAIL] signature invalid: {exc}")
        sys.exit(1)

    print("[OK] self-contained signature valid")
    print(f"[OK] review_id: {receipt['review_id']}")
    print(f"[OK] signer_identity: {receipt['signer_identity']}")
    print(f"[OK] signature_algorithm: {receipt['signature_algorithm']}")
    print(f"[OK] verification_mode: {receipt['verification_mode']}")
    print(f"[OK] embedded_public_key_sha256: {embedded_public_key_sha256}")
    print(f"[OK] key_id: {receipt['key_lifecycle']['key_id']}")
    print(f"[OK] valid_from: {receipt['key_lifecycle']['valid_from']}")
    print(f"[OK] valid_until: {receipt['key_lifecycle']['valid_until']}")
    print(f"[OK] revoked: {receipt['key_lifecycle']['revoked']}")


if __name__ == "__main__":
    main()
