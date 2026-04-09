#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

from qsp import run_session

def main() -> int:
parser = argparse.ArgumentParser()
parser.add_argument("--config", required=True)
parser.add_argument("--outdir", required=True)
args = parser.parse_args()

config_path = Path(args.config)
outdir = Path(args.outdir)
evidence_dir = outdir / "evidence"
evidence_dir.mkdir(parents=True, exist_ok=True)

config = json.loads(config_path.read_text(encoding="utf-8"))

metadata = {
    "repository": os.environ.get("GITHUB_REPOSITORY", ""),
    "commit_sha": os.environ.get("GITHUB_SHA", ""),
    "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
}

result = run_session(config=config, metadata=metadata)

transcript_path = evidence_dir / "transcript.json"
evidence_path = evidence_dir / "session_evidence.json"

transcript_path.write_text(
    json.dumps(result["transcript"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
evidence_path.write_text(
    json.dumps(result["evidence"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print(f"[OK] wrote {transcript_path}")
print(f"[OK] wrote {evidence_path}")
return 0

if name == "main":
raise SystemExit(main())
