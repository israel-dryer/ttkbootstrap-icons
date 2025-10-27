from __future__ import annotations

import argparse
import json
from importlib.resources import files
from pathlib import Path


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_from_base_assets(out_dir: Path) -> None:
    """Copy Lucide assets bundled with the base package into this provider.

    Reads `lucide.ttf` and `lucide.json` from `ttkbootstrap_icons.assets` and writes
    them to this provider's package directory as `fonts/lucide.ttf` and `glyphmap.json`.
    """
    base_assets = files("ttkbootstrap_icons.assets")
    font_bytes = base_assets.joinpath("lucide.ttf").read_bytes()
    json_text = base_assets.joinpath("lucide.json").read_text(encoding="utf-8")

    # Validate JSON parses
    json.loads(json_text)

    fonts_dir = out_dir / "fonts"
    write_bytes(fonts_dir / "lucide.ttf", font_bytes)
    write_text(out_dir / "glyphmap.json", json_text)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Lucide assets for ttkbootstrap-icons.")
    parser.add_argument(
        "--out-dir",
        help="Output package directory",
        default=str(Path(__file__).resolve().parents[1]),
    )
    args = parser.parse_args(argv)

    out = Path(args.out_dir)
    copy_from_base_assets(out)
    print(f"Wrote: {out / 'glyphmap.json'}")
    print(f"Font at: {out / 'fonts' / 'lucide.ttf'}")


def default_main():
    return main([])


if __name__ == "__main__":
    main()

