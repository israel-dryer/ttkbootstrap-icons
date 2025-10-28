#!/usr/bin/env python3
"""Sync the root README.md to the base package README.

Usage:
  python scripts/sync_readme.py [source] [dest]

Defaults:
  source: README.md (repo root)
  dest:   packages/ttkbootstrap-icons/README.md
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Sync root README to base package README")
    parser.add_argument("source", nargs="?", default="README.md", help="Source README path")
    parser.add_argument(
        "dest",
        nargs="?",
        default=str(Path("packages") / "ttkbootstrap-icons" / "README.md"),
        help="Destination README path",
    )
    args = parser.parse_args(argv)

    src = Path(args.source)
    dst = Path(args.dest)

    if not src.exists():
        print(f"Source not found: {src}", file=sys.stderr)
        return 1

    # Ensure destination directory exists
    dst.parent.mkdir(parents=True, exist_ok=True)

    content = src.read_text(encoding="utf-8")
    # Write only if different
    if dst.exists():
        existing = dst.read_text(encoding="utf-8")
        if existing == content:
            print(f"No changes. {dst} is already up to date.")
            return 0

    dst.write_text(content, encoding="utf-8")
    print(f"Synced {src} -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

