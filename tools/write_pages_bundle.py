#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "release"
SITE = ROOT / "site"


def copy_file(name: str) -> None:
    src = OUT / name
    dst = SITE / name
    if not src.exists():
        raise FileNotFoundError(f"missing required file: {src}")
    shutil.copy2(src, dst)
    print(f"[OK] copied {src} -> {dst}")


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)

    files = [
        "release_manifest.json",
        "release_manifest.json.sha256",
        "release_manifest.json.ots",
        "github_actions_receipt.json",
        "stage265-source-bundle.tar.gz",
    ]
    for name in files:
        copy_file(name)

    print("[OK] Pages bundle prepared")


if __name__ == "__main__":
    main()
