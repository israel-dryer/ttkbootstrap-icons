from __future__ import annotations

import argparse
from pathlib import Path

from ttkbootstrap_icons.tooling import (
    download_to,
    load_json,
    load_text,
    glyphmap_from_metadata,
    glyphmap_from_ttf,
    glyphmap_from_css,
    write_glyphmap,
    ensure_dir,
)


PRESETS = {
    # Ionicons v2 (classic font) via cdnjs
    "ion2": {
        "version": "2.0.1",
        "url": "https://cdnjs.cloudflare.com/ajax/libs/ionicons/{ver}/fonts/ionicons.ttf",
    },
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Ion Icons assets for ttkbootstrap-icons.")
    parser.add_argument("--font-url", help="URL to download the TTF font file")
    parser.add_argument("--font-file", help="Path to a local TTF font file")
    parser.add_argument("--map-url", help="URL to download official metadata JSON (optional)")
    parser.add_argument("--map-file", help="Path to local metadata JSON (optional)")
    parser.add_argument("--css-url", help="URL to a CSS file (optional; e.g., cdn ionicons.min.css)")
    parser.add_argument("--css-file", help="Path to a local CSS file or directory (optional)")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()), help="Use a known CDN font URL preset")
    parser.add_argument("--version", help="Override preset version (e.g., 2.0.1)")
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    # Acquire font file
    if args.font_file:
        font_path = Path(args.font_file)
    elif args.font_url:
        font_name = Path(args.font_url).name or "ionicons.ttf"
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
    mapping = None
    if args.map_file or args.map_url:
        data = load_json(args.map_file or args.map_url)
        mapping = glyphmap_from_metadata(data)
    elif args.css_file or args.css_url or args.preset:
        css_text = None
        if args.css_file or args.css_url:
            src = args.css_file or args.css_url
            # If a directory is given for --css-file, pick ionicons*.css inside
            if args.css_file and Path(src).exists() and Path(src).is_dir():
                cand = None
                for name in ["ionicons.min.css", "ionicons.css"]:
                    p = Path(src) / name
                    if p.exists():
                        cand = str(p)
                        break
                if not cand:
                    # fallback to first matching ionicons*.css
                    for p in Path(src).glob("ionicons*.css"):
                        cand = str(p)
                        break
                src = cand or src
            print(f"Using CSS: {src}")
            css_text = load_text(src)
        elif args.preset:
            # Try cdnjs ionicons.min.css for the chosen version
            ver = args.version or PRESETS[args.preset]["version"]
            css_url = f"https://cdnjs.cloudflare.com/ajax/libs/ionicons/{ver}/css/ionicons.min.css"
            try:
                print(f"Fetching CSS: {css_url}")
                css_text = load_text(css_url)
            except Exception:
                css_text = None
        if css_text:
            mapping = glyphmap_from_css(css_text, class_prefixes=("ion-ios-", "ion-md-", "ion-"))
            if mapping:
                sample = list(mapping.keys())[:10]
                print(f"Extracted {len(mapping)} names from CSS; sample: {sample}")
            else:
                print("CSS parsed but no icon mappings found; falling back to TTF cmap.")
    # Fallback to TTF if CSS/metadata missing or yielded no mappings
    if not mapping:
        mapping = glyphmap_from_ttf(font_path)

    write_glyphmap(pkg_root / "glyphmap.json", mapping)
    print(f"Wrote: {pkg_root / 'glyphmap.json'}")
    print(f"Font at: {font_path}")


if __name__ == "__main__":
    main()


def default_main():
    """Build using recommended defaults (ion2 preset)."""
    return main(["--preset", "ion2"])
