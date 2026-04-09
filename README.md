# Stage263: Verification URL (Public Proof)

## Overview

Stage263 introduces a **verification URL** mechanism.

This stage transforms:

- Internal evidence → Publicly verifiable URL

Anyone can verify:

- Execution result
- Generated artifacts
- Integrity of the process

via a simple web access.

---

## Key Concept

Receipt → URL → Public Verification

Instead of requiring local execution:

- Evidence is published
- Verification is accessible via URL
- Anyone can independently confirm results

---

## What This Stage Proves

- Execution result can be published deterministically
- Verification is accessible without local setup
- Evidence is bound to a public URL
- Reproducibility is externally observable

---

## Verification

GitHub Actions:

- Workflow: stage263-verification-url

Artifacts:

- github-pages
- stage263-verification-bundle

Public URL:

👉 GitHub Pages (see repository settings)

---

## Security Notice

All previously exposed keys are considered compromised and are no longer trusted.

A new Ed25519 key pair has been generated after the compromise response.

- Private key is kept out of version control
- Rotated public key is tracked for verification
- Previously exposed keys are permanently revoked

---

## Important Notes

This stage does NOT:

- Claim cryptographic superiority
- Replace existing verification standards

This stage DOES:

- Improve accessibility of verification
- Reduce friction for external reviewers

---

## Position in QSP

Stage263 extends:

- Stage262 (execution + evidence)

into:

- Public verification layer

---

## License

MIT License (2025)