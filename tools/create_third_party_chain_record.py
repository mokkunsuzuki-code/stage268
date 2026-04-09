#!/usr/bin/env python3
import argparse, json, hashlib, datetime
from pathlib import Path

CHAIN_DIR = Path("out/third_party_chain")
RECORDS_DIR = CHAIN_DIR / "records"
INDEX_PATH = CHAIN_DIR / "chain_index.json"

def sha256(data): return hashlib.sha256(data).hexdigest()
def now(): return datetime.datetime.utcnow().isoformat() + "Z"

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")

def load(path): return json.loads(path.read_text())

def init_index():
    if INDEX_PATH.exists(): return load(INDEX_PATH)
    idx = {"record_count":0,"latest_record_id":None,"latest_record_sha256":None,"records":[]}
    save(INDEX_PATH, idx)
    return idx

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--executor", required=True)
    p.add_argument("--bundle-path", required=True)
    p.add_argument("--result", required=True)
    args=p.parse_args()

    idx=init_index()
    rid=f"record_{idx['record_count']+1:04d}"

    payload={"executor":args.executor,"bundle":args.bundle_path,"result":args.result,"time":now()}
    payload_bytes=json.dumps(payload,sort_keys=True).encode()
    payload_hash=sha256(payload_bytes)

    rec={
        "record_id":rid,
        "prev_id":idx["latest_record_id"],
        "prev_hash":idx["latest_record_sha256"],
        "payload_hash":payload_hash,
        "payload":payload
    }

    rec_bytes=json.dumps(rec,sort_keys=True).encode()
    rec_hash=sha256(rec_bytes)

    path=RECORDS_DIR/f"{rid}.json"
    path.write_text(json.dumps(rec,indent=2))

    idx["record_count"]+=1
    idx["latest_record_id"]=rid
    idx["latest_record_sha256"]=rec_hash
    idx["records"].append({"id":rid,"hash":rec_hash})

    save(INDEX_PATH, idx)

    print("[OK]", rid, "created")

if __name__=="__main__": main()
