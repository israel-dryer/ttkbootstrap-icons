from __future__ import annotations

import argparse
from pathlib import Path

from ttkbootstrap_icons.tooling import (
    download_to,
    load_json,
    glyphmap_from_metadata,
    glyphmap_from_ttf,
    write_glyphmap,
    ensure_dir,
)


PRESETS = {
    # Remix Icon via jsdelivr
    "remix3": {
        "version": "3.5.0",
        "url": "https://cdn.jsdelivr.net/npm/remixicon@{ver}/fonts/remixicon.ttf",
    },
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Remix Icons assets for ttkbootstrap-icons.")
    parser.add_argument("--font-url", help="URL to download the TTF font file")
    parser.add_argument("--font-file", help="Path to a local TTF font file")
    parser.add_argument("--map-url", help="URL to download official metadata JSON (optional)")
    parser.add_argument("--map-file", help="Path to local metadata JSON (optional)")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()), help="Use a known CDN font URL preset")
    parser.add_argument("--version", help="Override preset version (e.g., 3.5.0)")
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    # Acquire font file
    if args.font_file:
        font_path = Path(args.font_file)
    elif args.font_url:
        font_name = Path(args.font_url).name or "remixicon.ttf"
        font_path = fonts_dir / font_name
        download_to(args.font_url, font_path)
    elif args.preset:
        preset = PRESETS[args.preset]
        ver = args.version or preset["version"]
        url = preset["url"].format(ver=ver)
        font_name = Path(url).name
        font_path = fonts_dir / font_name
        download_to(url, font_path)
    else:
        raise SystemExit("--font-url or --font-file is required")

    # Build glyphmap
    if args.map_file or args.map_url:
        data = load_json(args.map_file or args.map_url)
        mapping = glyphmap_from_metadata(data)
    else:
        mapping = glyphmap_from_ttf(font_path)

    write_glyphmap(pkg_root / "glyphmap.json", mapping)
    print(f"Wrote: {pkg_root / 'glyphmap.json'}")
    print(f"Font at: {font_path}")


if __name__ == "__main__":
    main()


def default_main():
    """Build using recommended defaults (remix3 preset)."""
    return main(["--preset", "remix3"])
