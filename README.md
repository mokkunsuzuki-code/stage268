# Stage265: Public Verification URL

MIT License Copyright (c) 2025 Motohiro Suzuki

## Overview

Stage265 publishes a browser-accessible verification URL through GitHub Pages.

This stage extends Stage264 by adding:

- public verification page
- URL-based access
- browser-side manifest and bundle integrity checks
- GitHub Actions linkage visibility
- public evidence hosting

## Core Idea

Stage264 made the evidence reproducible.

Stage265 makes the evidence publicly checkable through a stable verification URL.

This means a third party can:

- open a GitHub Pages URL
- inspect the evidence bundle
- verify manifest integrity
- verify bundle integrity
- verify GitHub Actions linkage

without requiring a local repository checkout for the basic verification path.

## Key Files

- `site/index.html`
- `site/verify.html`
- `release_manifest.json`
- `release_manifest.json.sha256`
- `release_manifest.json.ots`
- `github_actions_receipt.json`
- `stage265-source-bundle.tar.gz`

## Workflow

GitHub Actions builds the evidence bundle, prepares the Pages site, and deploys it.

## Public Verification URL

After Pages deployment, the expected URL format is:

```text
https://mokkunsuzuki-code.github.io/stage265/

Main verification page:

https://mokkunsuzuki-code.github.io/stage265/verify.html
Important Accuracy

Browser verification in Stage265 confirms:

manifest presence
manifest SHA-256 integrity
bundle SHA-256 integrity
receipt presence
Actions run linkage
OTS proof presence

It does not by itself finalize Bitcoin confirmation of the OpenTimestamps proof.

License

This project is licensed under the MIT License.
