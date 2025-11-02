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
    # Font Awesome 6 Free via cdnjs
    # styles: solid, regular, brands – generator supports a single TTF; default to solid
    "fa6-solid": {
        "version": "6.5.2",
        "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{ver}/webfonts/fa-solid-900.ttf",
    },
    "fa6-regular": {
        "version": "6.5.2",
        "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{ver}/webfonts/fa-regular-400.ttf",
    },
    "fa6-brands": {
        "version": "6.5.2",
        "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{ver}/webfonts/fa-brands-400.ttf",
    },
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Font Awesome assets for ttkbootstrap-icons.")
    parser.add_argument("--font-url", help="URL to download the TTF font file")
    parser.add_argument("--font-file", help="Path to a local TTF font file")
    parser.add_argument("--map-url", help="URL to download official metadata JSON (optional)")
    parser.add_argument("--map-file", help="Path to local metadata JSON (optional)")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS.keys()),
        help="Use a known CDN font URL preset (choose style)",
    )
    parser.add_argument(
        "--version",
        help="Override preset version (e.g., 6.5.2)",
    )
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    # Determine style from preset
    style = None
    if args.preset:
        # Extract style from preset name (e.g., "fa6-solid" -> "solid")
        style = args.preset.split("-", 1)[1] if "-" in args.preset else None

    # Acquire font file
    font_path = None
    if args.font_file:
        font_path = Path(args.font_file)
    elif args.font_url:
        font_name = Path(args.font_url).name or "fontawesome.ttf"
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

    # Write glyphmap with appropriate filename
    # For Font Awesome with multiple font files, use glyphmap-{style}.json
    if style:
        glyphmap_path = pkg_root / f"glyphmap-{style}.json"
    else:
        glyphmap_path = pkg_root / "glyphmap.json"

    write_glyphmap(glyphmap_path, mapping)
    print(f"Wrote: {glyphmap_path}")
    print(f"Font at: {font_path}")


if __name__ == "__main__":
    main()


def default_main():
    """Build using recommended defaults (all three Font Awesome styles)."""
    print("Generating Font Awesome assets for all styles...")
    for preset in ["fa6-solid", "fa6-regular", "fa6-brands"]:
        print(f"\nGenerating {preset}...")
        main(["--preset", preset])
