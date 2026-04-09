#!/usr/bin/env bash
set -euo pipefail

rm -rf out/third_party_chain out/anchors
mkdir -p out/third_party_chain/records out/anchors

chmod +x tools/run_stage257.sh
./tools/run_stage257.sh

python3 tools/build_stage258_anchor_bundle.py
python3 tools/verify_stage258_anchor.py

echo
echo "[DONE] Stage258 external anchor bundle completed"
