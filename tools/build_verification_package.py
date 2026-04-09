#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

def sha256_file(path: Path) -> str:
h = hashlib.sha256()
with path.open("rb") as f:
while True:
chunk = f.read(65536)
if not chunk:
break
h.update(chunk)
return h.hexdigest()

def main() -> int:
parser = argparse.ArgumentParser()
parser.add_argument("--evidence", required=True)
parser.add_argument("--transcript", required=True)
parser.add_argument("--outdir", required=True)
parser.add_argument("--repo", default="")
parser.add_argument("--commit", default="")
parser.add_argument("--run-id", default="local")
parser.add_argument("--pages-url", default="")
args = parser.parse_args()

evidence_path = Path(args.evidence)
transcript_path = Path(args.transcript)
outdir = Path(args.outdir)
verify_dir = outdir / "verification"
verify_dir.mkdir(parents=True, exist_ok=True)

manifest = {
    "stage": 263,
    "protocol": "QSP",
    "verification_url": args.pages_url,
    "repository": args.repo,
    "commit_sha": args.commit,
    "run_id": args.run_id,
    "artifacts": {
        "session_evidence": {
            "path": "artifacts/session_evidence.json",
            "sha256": sha256_file(evidence_path),
        },
        "transcript": {
            "path": "artifacts/transcript.json",
            "sha256": sha256_file(transcript_path),
        },
        "verification_script": {
            "path": "artifacts/verify_stage263.py",
        },
    },
    "local_verify_command": (
        "python3 tools/verify_stage263.py "
        "--evidence out/stage263/evidence/session_evidence.json "
        "--transcript out/stage263/evidence/transcript.json "
        "--manifest out/stage263/verification/verification_manifest.json "
        "--manifest-sha256 out/stage263/verification/verification_manifest.sha256.txt"
    ),
}

manifest_path = verify_dir / "verification_manifest.json"
manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
manifest_path.write_bytes(manifest_bytes)

manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
manifest_sha256_path = verify_dir / "verification_manifest.sha256.txt"
manifest_sha256_path.write_text(
    f"{manifest_sha256}  verification_manifest.json\n",
    encoding="utf-8",
)

url_path = verify_dir / "verification_url.txt"
url_path.write_text((args.pages_url + "\n") if args.pages_url else "\n", encoding="utf-8")

print(f"[OK] wrote {manifest_path}")
print(f"[OK] wrote {manifest_sha256_path}")
print(f"[OK] wrote {url_path}")
return 0

if name == "main":
raise SystemExit(main())
