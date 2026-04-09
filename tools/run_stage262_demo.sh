#!/bin/bash
set -euo pipefail

echo "[1/3] Generating keys"
python3 tools/generate_keys.py

echo "[2/3] Creating self-contained reviewer receipt"
python3 tools/create_self_contained_receipt.py

echo "[3/3] Verifying self-contained reviewer receipt"
python3 tools/verify_receipt_self_contained.py out/receipts/review_receipt_self_contained.json

echo "[DONE] Stage262 demo complete"
