# Stage265: Public Verification URL

## Overview

Stage265 publishes a public verification page through GitHub Pages.

This stage extends Stage264 by adding:

- a browser-accessible verification URL
- public hosting for manifest / sha256 / receipt / ots / bundle
- verification without requiring local Python execution for basic checks

## What this stage proves

A verifier can open a URL and confirm:

- the manifest exists
- the manifest SHA-256 matches
- the bundle SHA-256 matches the manifest claim
- the GitHub Actions receipt contains a public run URL
- the OpenTimestamps proof file is present

## Important note

Browser-side verification does not replace final OpenTimestamps blockchain confirmation.

For final OTS confirmation, a verifier may still run:

```bash
ots upgrade release_manifest.json.ots
ots verify release_manifest.json.ots
Why this matters

This stage moves from:

downloadable evidence

to

directly accessible public verification via URL
