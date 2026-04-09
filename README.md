# Stage263: QSP Execution → Evidence → Verification URL

Stage263 turns QSP from a local proof artifact into a **publicly reviewable verification surface**.

This stage adds:

- actual QSP session execution
- deterministic evidence generation
- local verification from evidence
- public verification URL via GitHub Pages
- fail-closed verification checks

## What This Stage Proves

Stage263 proves the following chain:

QSP execution  
→ evidence is generated automatically  
→ evidence is verified automatically  
→ verification artifacts are published at a public URL

This is the first stage where the system is presented as a **whole verification path**, not only as isolated evidence fragments.

## Core Idea

The important change is:

- before Stage263: evidence existed
- in Stage263: **execution itself produces reviewable public proof**

That means a reviewer can check:

1. the session transcript
2. the derived evidence hashes
3. the verification manifest
4. the public verification page
5. the local verification script result

## Repository Structure

- `configs/stage263_session.json`  
  deterministic input used by the QSP execution demo

- `qsp/session.py`  
  minimal QSP execution model for Stage263

- `tools/run_stage263_qsp.py`  
  runs the session and emits evidence

- `tools/build_verification_package.py`  
  builds verification manifest and sha256 files

- `tools/verify_stage263.py`  
  verifies transcript hash, derived secret hash, evidence hash, manifest hash

- `tools/generate_verification_page.py`  
  creates `site/index.html` and publishes verification artifacts

- `.github/workflows/stage263-verification-url.yml`  
  CI pipeline for execution, verification, artifact publication, and GitHub Pages deploy

## Local Run

```bash
chmod +x tools/run_stage263_qsp.sh
./tools/run_stage263_qsp.sh

Expected result:

out/stage263/evidence/session_evidence.json
out/stage263/evidence/transcript.json
out/stage263/verification/verification_manifest.json
out/stage263/verification/verification_manifest.sha256.txt
site/index.html
Local Verification
python3 tools/verify_stage263.py \
  --evidence out/stage263/evidence/session_evidence.json \
  --transcript out/stage263/evidence/transcript.json \
  --manifest out/stage263/verification/verification_manifest.json \
  --manifest-sha256 out/stage263/verification/verification_manifest.sha256.txt

Expected output:

[OK] transcript hash matches
[OK] derived secret hash matches
[OK] evidence hash matches manifest
[OK] manifest sha256 file matches
[OK] Stage263 verification complete
Public Verification URL

After GitHub Actions succeeds, GitHub Pages publishes the review page.

Expected URL:

https://mokkunsuzuki-code.github.io/stage263/

The public page contains:

summary of the run
commit / run identifiers
evidence sha256
links to downloadable verification artifacts
local verification command for independent reviewers
Security Meaning

This stage does not claim a new cryptographic proof.

It proves something narrower and more honest:

QSP execution is bound to generated evidence
evidence is bound to a manifest
manifest is bound to a public verification page
verification fails closed on mismatch

So the trust moves further away from:

“please trust this key”

and closer to:

“run verification against the published evidence”
Limitations

This repository is still a research-stage verification framework.

It does not claim:

production deployment readiness
formal proof of all protocol properties
universal security beyond the stated execution model

It does claim:

deterministic evidence generation
reproducible verification
public reviewability
fail-closed mismatch detection
5-Minute Review Path
Open the GitHub Pages verification URL
Download session_evidence.json, transcript.json, and verification_manifest.json
Run tools/verify_stage263.py
Confirm all checks return [OK]
License

MIT License
