#!/usr/bin/env python3
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import pathlib
import subprocess
import tarfile
from datetime import datetime, timezone


ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "out" / "release"
BUNDLE_PATH = OUT_DIR / "stage265-source-bundle.tar.gz"
MANIFEST_PATH = OUT_DIR / "release_manifest.json"
SHA256_PATH = OUT_DIR / "release_manifest.json.sha256"


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True).strip()


def try_run(cmd: list[str], default: str = "") -> str:
    try:
        return run(cmd)
    except Exception:
        return default


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tracked_files() -> list[pathlib.Path]:
    files = run(["git", "ls-files"]).splitlines()
    result: list[pathlib.Path] = []
    for rel in files:
        p = ROOT / rel
        if not p.is_file():
            continue
        if rel.startswith("out/"):
            continue
        if rel.startswith(".git/"):
            continue
        if "__pycache__" in rel:
            continue
        result.append(p)
    return sorted(result, key=lambda x: x.relative_to(ROOT).as_posix())


def build_deterministic_bundle(bundle_path: pathlib.Path) -> str:
    bundle_path.parent.mkdir(parents=True, exist_ok=True)

    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for path in tracked_files():
            rel = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()

            info = tarfile.TarInfo(name=rel)
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""

            tar.addfile(info, io.BytesIO(data))

    raw.seek(0)
    with gzip.GzipFile(filename="", mode="wb", fileobj=bundle_path.open("wb"), mtime=0) as gz:
        gz.write(raw.getvalue())

    return sha256_file(bundle_path)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    commit = try_run(["git", "rev-parse", "HEAD"], "unknown")
    short_commit = commit[:12] if commit != "unknown" else "unknown"
    branch = try_run(["git", "rev-parse", "--abbrev-ref", "HEAD"], "unknown")
    repo_url = try_run(["git", "config", "--get", "remote.origin.url"], "unknown")
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    bundle_sha256 = build_deterministic_bundle(BUNDLE_PATH)

    manifest = {
        "version": 1,
        "stage": "stage265",
        "title": "Public Verification URL with GitHub Pages and reproducible evidence bundle",
        "generated_at_utc": generated_at,
        "repository": {
            "remote": repo_url,
            "branch": branch,
            "commit": commit,
            "short_commit": short_commit,
        },
        "artifacts": [
            {
                "path": str(BUNDLE_PATH.relative_to(ROOT)),
                "sha256": bundle_sha256,
                "description": "Deterministic source bundle derived from tracked repository files",
            }
        ],
        "github_actions_context": {
            "workflow": os.getenv("GITHUB_WORKFLOW", ""),
            "run_id": os.getenv("GITHUB_RUN_ID", ""),
            "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT", ""),
            "sha": os.getenv("GITHUB_SHA", ""),
            "ref": os.getenv("GITHUB_REF", ""),
            "actor": os.getenv("GITHUB_ACTOR", ""),
            "repository": os.getenv("GITHUB_REPOSITORY", ""),
            "server_url": os.getenv("GITHUB_SERVER_URL", ""),
        },
        "notes": [
            "The manifest binds the source bundle hash to a specific repository state.",
            "OpenTimestamps stamps the manifest file itself.",
            "GitHub Actions receipt provides execution-time evidence for independent review.",
            "GitHub Pages publishes a public verification URL for browser-based checking."
        ],
    }

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    manifest_sha256 = sha256_file(MANIFEST_PATH)
    SHA256_PATH.write_text(
        f"{manifest_sha256}  {MANIFEST_PATH.name}\n",
        encoding="utf-8",
    )

    print("[OK] Built deterministic source bundle")
    print(f"[OK] bundle: {BUNDLE_PATH}")
    print(f"[OK] bundle_sha256: {bundle_sha256}")
    print(f"[OK] manifest: {MANIFEST_PATH}")
    print(f"[OK] manifest_sha256: {manifest_sha256}")
    print(f"[OK] sha256 file: {SHA256_PATH}")


if __name__ == "__main__":
    main()
