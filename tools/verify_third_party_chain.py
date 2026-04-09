#!/usr/bin/env python3
import json, hashlib, sys
from pathlib import Path

CHAIN_DIR = Path("out/third_party_chain")
INDEX_PATH = CHAIN_DIR / "chain_index.json"

def sha256(data): return hashlib.sha256(data).hexdigest()

def main():
    idx=json.loads(INDEX_PATH.read_text())
    prev_id=None
    prev_hash=None

    for i,r in enumerate(idx["records"],1):
        path=CHAIN_DIR/"records"/f"record_{i:04d}.json"
        if not path.exists():
            print("[FAIL] missing", path); sys.exit(1)

        rec=json.loads(path.read_text())
        rec_hash=sha256(json.dumps(rec,sort_keys=True).encode())

        if rec["prev_id"]!=prev_id:
            print("[FAIL] chain broken (id)"); sys.exit(1)
        if rec["prev_hash"]!=prev_hash:
            print("[FAIL] chain broken (hash)"); sys.exit(1)

        prev_id=rec["record_id"]
        prev_hash=rec_hash

    print("[OK] chain verified")

if __name__=="__main__": main()
