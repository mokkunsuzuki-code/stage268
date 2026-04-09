#!/usr/bin/env bash
set -euo pipefail

OUTDIR="out/stage263"
SITE_DIR="site"

REPO="${GITHUB_REPOSITORY:-mokkunsuzuki-code/stage263}"
COMMIT="${GITHUB_SHA:-local}"
RUN_ID="${GITHUB_RUN_ID:-local}"

OWNER="${REPO%%/}"
REPO_NAME="${REPO##/}"
PAGES_URL="https://${OWNER}.github.io/${REPO_NAME}/"

rm -rf "${OUTDIR}" "${SITE_DIR}"
mkdir -p "${OUTDIR}" "${SITE_DIR}"

python3 tools/run_stage263_qsp.py
--config configs/stage263_session.json
--outdir "${OUTDIR}"

python3 tools/build_verification_package.py
--evidence "${OUTDIR}/evidence/session_evidence.json"
--transcript "${OUTDIR}/evidence/transcript.json"
--outdir "${OUTDIR}"
--repo "${REPO}"
--commit "${COMMIT}"
--run-id "${RUN_ID}"
--pages-url "${PAGES_URL}"

python3 tools/verify_stage263.py
--evidence "${OUTDIR}/evidence/session_evidence.json"
--transcript "${OUTDIR}/evidence/transcript.json"
--manifest "${OUTDIR}/verification/verification_manifest.json"
--manifest-sha256 "${OUTDIR}/verification/verification_manifest.sha256.txt"

python3 tools/generate_verification_page.py
--evidence "${OUTDIR}/evidence/session_evidence.json"
--transcript "${OUTDIR}/evidence/transcript.json"
--manifest "${OUTDIR}/verification/verification_manifest.json"
--manifest-sha256 "${OUTDIR}/verification/verification_manifest.sha256.txt"
--site-dir "${SITE_DIR}"

echo
echo "[OK] Stage263 local run completed"
echo "[OK] verification URL (after Pages deploy): ${PAGES_URL}"
