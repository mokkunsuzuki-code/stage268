#!/usr/bin/env python3
import argparse
import html
import json
import shutil
from pathlib import Path

def copy_file(src: Path, dst: Path) -> None:
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src, dst)

def main() -> int:
parser = argparse.ArgumentParser()
parser.add_argument("--evidence", required=True)
parser.add_argument("--transcript", required=True)
parser.add_argument("--manifest", required=True)
parser.add_argument("--manifest-sha256", required=True)
parser.add_argument("--site-dir", required=True)
args = parser.parse_args()

evidence_path = Path(args.evidence)
transcript_path = Path(args.transcript)
manifest_path = Path(args.manifest)
manifest_sha_path = Path(args.manifest_sha256)
site_dir = Path(args.site_dir)

site_dir.mkdir(parents=True, exist_ok=True)
artifacts_dir = site_dir / "artifacts"
artifacts_dir.mkdir(parents=True, exist_ok=True)

copy_file(evidence_path, artifacts_dir / "session_evidence.json")
copy_file(transcript_path, artifacts_dir / "transcript.json")
copy_file(manifest_path, artifacts_dir / "verification_manifest.json")
copy_file(manifest_sha_path, artifacts_dir / "verification_manifest.sha256.txt")
copy_file(Path("tools/verify_stage263.py"), artifacts_dir / "verify_stage263.py")

evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

verification_url = manifest.get("verification_url", "")
repo = manifest.get("repository", "")
commit_sha = manifest.get("commit_sha", "")
run_id = manifest.get("run_id", "")
evidence_sha = manifest["artifacts"]["session_evidence"]["sha256"]
transcript_sha = manifest["artifacts"]["transcript"]["sha256"]
local_verify_command = manifest.get("local_verify_command", "")

html_text = f"""<!doctype html>
<html lang="en"> <head> <meta charset="utf-8"> <title>Stage263 Verification URL</title> <meta name="viewport" content="width=device-width, initial-scale=1"> <style> body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem auto; max-width: 900px; line-height: 1.6; padding: 0 1rem; }} code, pre {{ background: #f5f5f5; padding: 0.2rem 0.4rem; border-radius: 6px; }} pre {{ overflow-x: auto; padding: 1rem; }} .card {{ border: 1px solid #ddd; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1rem; }} a {{ text-decoration: none; }} </style> </head> <body> <h1>Stage263 Verification URL</h1> <div class="card"> <p><strong>Protocol:</strong> {html.escape(str(evidence.get("protocol", "")))}</p> <p><strong>Stage:</strong> {html.escape(str(evidence.get("stage", "")))}</p> <p><strong>Session ID:</strong> {html.escape(str(evidence.get("session_id", "")))}</p> <p><strong>Status:</strong> {html.escape(str(evidence.get("result", {}).get("status", "")))}</p> <p><strong>Fail-Closed:</strong> {html.escape(str(evidence.get("fail_closed", "")))}</p> <p><strong>Repository:</strong> {html.escape(repo)}</p> <p><strong>Commit:</strong> <code>{html.escape(commit_sha)}</code></p> <p><strong>Run ID:</strong> {html.escape(str(run_id))}</p> <p><strong>Verification URL:</strong> <a href="{html.escape(verification_url)}">{html.escape(verification_url)}</a></p> </div> <div class="card"> <h2>Artifact Hashes</h2> <p><strong>session_evidence.json</strong><br><code>{html.escape(evidence_sha)}</code></p> <p><strong>transcript.json</strong><br><code>{html.escape(transcript_sha)}</code></p> </div> <div class="card"> <h2>Download Artifacts</h2> <ul> <li><a href="./artifacts/session_evidence.json">session_evidence.json</a></li> <li><a href="./artifacts/transcript.json">transcript.json</a></li> <li><a href="./artifacts/verification_manifest.json">verification_manifest.json</a></li> <li><a href="./artifacts/verification_manifest.sha256.txt">verification_manifest.sha256.txt</a></li> <li><a href="./artifacts/verify_stage263.py">verify_stage263.py</a></li> </ul> </div> <div class="card"> <h2>Independent Local Verification</h2> <pre>{html.escape(local_verify_command)}</pre> </div> <div class="card"> <h2>What This Proves</h2> <p> Stage263 binds QSP execution, transcript evidence, verification manifest, and public review URL into one chain. Verification is expected to fail closed on mismatch. </p> </div> </body> </html> """ (site_dir / "index.html").write_text(html_text, encoding="utf-8") print(f"[OK] wrote {site_dir / 'index.html'}") return 0

if name == "main":
raise SystemExit(main())
