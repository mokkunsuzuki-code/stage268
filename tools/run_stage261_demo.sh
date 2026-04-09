#!/bin/bash
set -euo pipefail

echo "[1/3] Generating keys"
python3 tools/generate_keys.py

echo "[2/3] Creating signed reviewer receipt"
python3 tools/create_receipt.py

echo "[3/3] Verifying signed reviewer receipt"
python3 tools/verify_receipt.py out/receipts/review_receipt.json

echo "[DONE] Stage261 demo complete"
