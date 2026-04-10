# Stage264: World-Class Proof Structure
## release_manifest.json + OpenTimestamps + GitHub Actions Receipt

MIT License Copyright (c) 2025 Motohiro Suzuki

## Overview

Stage264 integrates three public proof layers into one reproducible verification structure:

1. `release_manifest.json`
2. `release_manifest.json.ots`
3. `github_actions_receipt.json`

This stage is designed to prove, in a third-party verifiable way:

- what artifact was produced
- what exact hash was bound to it
- that the manifest was timestamped through OpenTimestamps
- that the same proof-generation flow ran inside GitHub Actions
- that the resulting evidence can be downloaded and re-verified outside GitHub

This is not just “a file exists.”
It is a structure for proving:

- **what**
- **when**
- **where**
- **under which workflow execution**
- **with reproducible verification**

---

## What This Stage Adds

Stage264 adds:

- deterministic `release_manifest.json` generation
- SHA-256 sidecar generation for the manifest
- OpenTimestamps stamping for the manifest
- GitHub Actions receipt generation
- verification logic for downloaded external artifacts
- artifact upload for independent re-verification

This transforms:

- local proof only  
into
- local proof + CI proof + downloadable external verification proof

---

## Proof Components

### 1. `release_manifest.json`

This file defines the released artifact set and binds each artifact to a SHA-256 digest.

It answers:

- What was produced?
- Which exact repository state does it correspond to?
- Which artifact hash is being claimed?

---

### 2. `release_manifest.json.sha256`

This sidecar file allows a verifier to confirm the integrity of the manifest itself.

It answers:

- Has the manifest changed?
- Does the manifest hash match the claimed value?

---

### 3. `release_manifest.json.ots`

This is the OpenTimestamps proof for the manifest.

It answers:

- Did this exact manifest exist at or before the submitted timestamping event?

Important note:

- immediately after stamping, `.ots` may still show  
  `Pending confirmation in Bitcoin blockchain`
- this is normal
- later upgrade/final verification strengthens the timestamp proof further

---

### 4. `github_actions_receipt.json`

This file records GitHub Actions execution context such as:

- workflow name
- repository
- run ID
- run URL
- commit SHA
- ref
- actor

It answers:

- Was the proof-generation process executed in CI?
- Which run produced the evidence?
- Which public workflow execution is tied to the generated files?

---

### 5. Uploaded Artifact Bundle

GitHub Actions uploads a downloadable artifact bundle containing:

- `release_manifest.json`
- `release_manifest.json.sha256`
- `release_manifest.json.ots`
- `github_actions_receipt.json`
- `stage264-source-bundle.tar.gz`

This allows a third party to:

- download the evidence
- verify the hashes
- verify the manifest structure
- verify the Actions run linkage
- verify outside the repository owner’s local machine

---

## Why This Stage Matters

This stage moves the project from:

- “the owner generated evidence locally”

to:

- “the same structure was generated in GitHub Actions”
- “the evidence can be downloaded by a third party”
- “the downloaded evidence can be re-verified independently”
- “the manifest can be externally timestamped”

That is why Stage264 is a major step toward a **world-class proof structure**.

---

## Repository Structure

```text
.github/workflows/stage264-release-manifest-ots.yml
docs/stage264_world_class_proof_structure.md
tools/build_release_manifest.py
tools/stamp_manifest_ots.sh
tools/write_github_actions_receipt.py
tools/verify_stage264_anchor.py
tools/run_stage264_manifest_anchor.sh
out/release/
Local Run

Install OpenTimestamps client:

python3 -m pip install --user opentimestamps-client

Run the full Stage264 flow locally:

./tools/run_stage264_manifest_anchor.sh

Expected outputs:

out/release/release_manifest.json
out/release/release_manifest.json.sha256
out/release/release_manifest.json.ots
out/release/github_actions_receipt.json
out/release/stage264-source-bundle.tar.gz
GitHub Actions Workflow

Workflow:

stage264-release-manifest-ots

This workflow:

checks out the repository
sets up Python
installs OpenTimestamps client
builds the release manifest
stamps the manifest with OpenTimestamps
writes the GitHub Actions receipt
verifies the generated structure
uploads the resulting proof bundle as an artifact
Verification
Verify local outputs
python3 tools/verify_stage264_anchor.py \
  --dir out/release \
  --ots-bin "$(command -v ots)"
Download GitHub Actions artifact
RUN_ID=$(gh run list --workflow "stage264-release-manifest-ots" --limit 1 --json databaseId --jq '.[0].databaseId')

mkdir -p downloaded_stage264_anchor

gh run download "$RUN_ID" -n stage264-release-anchor -D downloaded_stage264_anchor
Verify downloaded artifact bundle
python3 tools/verify_stage264_anchor.py \
  --dir downloaded_stage264_anchor \
  --ots-bin "$(command -v ots)"

This verification confirms:

artifact hash integrity
manifest hash integrity
GitHub Actions run linkage
OpenTimestamps proof presence
external re-verifiability
Important Accuracy Notes

Stage264 does not claim:

immediate final Bitcoin confirmation at stamp time
immutable blockchain finality at the exact moment .ots is first generated
that OpenTimestamps alone proves build correctness

Stage264 does claim:

deterministic artifact binding through the manifest
manifest integrity checking through SHA-256
timestamp-proof generation through OpenTimestamps
CI execution evidence through GitHub Actions receipt
external downloadable re-verification
Security Meaning

Stage264 proves a stronger chain of evidence:

source state
deterministic bundle
manifest binding
hash integrity
timestamp submission
CI execution record
downloadable artifact proof
third-party re-verification

This is much stronger than ordinary repository publication.

Result

Stage264 establishes a public proof structure where a third party can verify:

what was claimed
which artifact hash was bound
which workflow run produced the evidence
that the timestamp proof exists
that the evidence can be re-checked outside the owner’s machine

That is the core reason Stage264 represents a world-level proof structure step for QSP-related assurance work.

License

This project is licensed under the MIT License.