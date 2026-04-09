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
    "verification_method",
    "verification_material",
    "key_lifecycle",
    "content",
    "signature",
}


def canonical_json_bytes(obj: dict) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 tools/verify_receipt.py <receipt.json>")
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

    signature_hex = receipt.get("signature")
    if not isinstance(signature_hex, str) or not signature_hex:
        print("[FAIL] invalid signature field")
        sys.exit(1)

    algorithm = receipt.get("signature_algorithm")
    if algorithm != "Ed25519":
        print(f"[FAIL] unsupported signature_algorithm: {algorithm}")
        sys.exit(1)

    verification_material = receipt.get("verification_material", {})
    public_key_path = verification_material.get("public_key_path")
    if not public_key_path:
        print("[FAIL] missing verification_material.public_key_path")
        sys.exit(1)

    public_key_file = Path(public_key_path)
    if not public_key_file.exists():
        print(f"[FAIL] public key not found: {public_key_file}")
        sys.exit(1)

    public_key = serialization.load_pem_public_key(public_key_file.read_bytes())

    unsigned_receipt = dict(receipt)
    signature = bytes.fromhex(unsigned_receipt.pop("signature"))

    try:
        public_key.verify(signature, canonical_json_bytes(unsigned_receipt))
    except Exception as exc:
        print(f"[FAIL] signature invalid: {exc}")
        sys.exit(1)

    print("[OK] signature valid")
    print(f"[OK] review_id: {receipt['review_id']}")
    print(f"[OK] signer_identity: {receipt['signer_identity']}")
    print(f"[OK] signature_algorithm: {receipt['signature_algorithm']}")
    print(f"[OK] key_id: {receipt['key_lifecycle']['key_id']}")
    print(f"[OK] valid_from: {receipt['key_lifecycle']['valid_from']}")
    print(f"[OK] valid_until: {receipt['key_lifecycle']['valid_until']}")
    print(f"[OK] revoked: {receipt['key_lifecycle']['revoked']}")


if __name__ == "__main__":
    main()
