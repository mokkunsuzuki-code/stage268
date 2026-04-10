#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[*] Building release manifest..."
python3 tools/build_release_manifest.py

echo "[*] Stamping release manifest with OpenTimestamps..."
bash tools/stamp_manifest_ots.sh

echo "[*] Writing GitHub Actions receipt..."
python3 tools/write_github_actions_receipt.py

echo "[*] Local verification..."

if [[ -n "${OTS_BIN:-}" && -x "${OTS_BIN:-}" ]]; then
  FOUND_OTS="$OTS_BIN"
elif command -v ots >/dev/null 2>&1; then
  FOUND_OTS="$(command -v ots)"
elif command -v pyenv >/dev/null 2>&1 && pyenv which ots >/dev/null 2>&1; then
  FOUND_OTS="$(pyenv which ots)"
else
  FOUND_OTS=""
fi

if [[ -n "$FOUND_OTS" ]]; then
  python3 tools/verify_stage264_anchor.py --dir out/release --ots-bin "$FOUND_OTS"
else
  python3 tools/verify_stage264_anchor.py --dir out/release
fi

echo "[*] Preparing Pages bundle..."
python3 tools/write_pages_bundle.py

echo "[OK] Stage265 public verification flow completed"
