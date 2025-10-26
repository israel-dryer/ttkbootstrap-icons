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
    # Simple Icons Font via jsdelivr/unpkg or raw GitHub
    "simple": {
        "version": "latest",
        # We'll try multiple candidates for CSS and TTF below
    },
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Simple Icons assets for ttkbootstrap-icons.")
    parser.add_argument("--font-url", help="URL to download the TTF font file")
    parser.add_argument("--font-file", help="Path to a local TTF font file")
    parser.add_argument("--map-url", help="URL to download official metadata JSON (optional)")
    parser.add_argument("--map-file", help="Path to local metadata JSON (optional)")
    parser.add_argument("--css-url", help="URL to a CSS file (optional)")
    parser.add_argument("--css-file", help="Path to a local CSS file or directory (optional)")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()), help="Use a known CDN font URL preset")
    parser.add_argument("--version", help="Override preset version")
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    # Acquire font file
    if args.font_file:
        font_path = Path(args.font_file)
    elif args.font_url:
        font_name = Path(args.font_url).name or "SimpleIcons.ttf"
        font_path = fonts_dir / font_name
        download_to(args.font_url, font_path)
    elif args.preset:
        ver = args.version or PRESETS[args.preset].get("version", "latest")
        # Try several CDN/raw locations
        font_candidates = [
            f"https://cdn.jsdelivr.net/npm/simple-icons-font@{ver}/fonts/SimpleIcons.ttf",
            f"https://cdn.jsdelivr.net/npm/simple-icons-font@{ver}/font/SimpleIcons.ttf",
            f"https://unpkg.com/simple-icons-font@{ver}/fonts/SimpleIcons.ttf",
            f"https://raw.githubusercontent.com/simple-icons/simple-icons-font/main/fonts/SimpleIcons.ttf",
            f"https://raw.githubusercontent.com/simple-icons/simple-icons-font/main/font/SimpleIcons.ttf",
        ]
        last_err = None
        font_path = None
        for url in font_candidates:
            try:
                font_name = Path(url).name
                dest = fonts_dir / font_name
                download_to(url, dest)
                font_path = dest
                break
            except Exception as e:
                last_err = e
                continue
        if not font_path:
            raise SystemExit(f"Failed to download Simple Icons font. Last error: {last_err}")
    else:
        raise SystemExit("--font-url or --font-file is required")

    # Build glyphmap
    mapping = None
    if args.map_file or args.map_url:
        data = load_json(args.map_file or args.map_url)
        mapping = glyphmap_from_metadata(data)
    else:
        # Try CSS for readable names
        css_text = None
        if args.css_file or args.css_url:
            src = args.css_file or args.css_url
            # If directory passed, pick common names
            if args.css_file and Path(src).exists() and Path(src).is_dir():
                cand = None
                for name in [
                    "simple-icons.css",
                    "simple-icons.min.css",
                    "SimpleIcons.css",
                ]:
                    p = Path(src) / name
                    if p.exists():
                        cand = str(p)
                        break
                if not cand:
                    for p in Path(src).glob("*simple*icons*.css"):
                        cand = str(p)
                        break
                src = cand or src
            print(f"Using CSS: {src}")
            css_text = load_text(src)
        elif args.preset:
            css_candidates = [
                f"https://cdn.jsdelivr.net/npm/simple-icons-font@{ver}/css/simple-icons.min.css",
                f"https://cdn.jsdelivr.net/npm/simple-icons-font@{ver}/simple-icons.min.css",
                f"https://cdn.jsdelivr.net/npm/simple-icons-font@{ver}/simple-icons.css",
                f"https://unpkg.com/simple-icons-font@{ver}/css/simple-icons.min.css",
                f"https://raw.githubusercontent.com/simple-icons/simple-icons-font/main/css/simple-icons.css",
            ]
            for url in css_candidates:
                try:
                    print(f"Fetching CSS: {url}")
                    css_text = load_text(url)
                    break
                except Exception:
                    continue
        if css_text:
            # Common prefix appears to be 'si-'
            mapping = glyphmap_from_css(css_text, class_prefixes=("si-", "simple-icons-", "simpleicons-"))
            if mapping:
                sample = list(mapping.keys())[:10]
                print(f"Extracted {len(mapping)} names from CSS; sample: {sample}")
            else:
                print("CSS parsed but no icon mappings found; using TTF cmap as fallback.")
    if not mapping:
        mapping = glyphmap_from_ttf(font_path)

    write_glyphmap(pkg_root / "glyphmap.json", mapping)
    print(f"Wrote: {pkg_root / 'glyphmap.json'}")
    print(f"Font at: {font_path}")


if __name__ == "__main__":
    main()


def default_main():
    """Quick build for Simple Icons.

    Since there is no official font preset, this looks for a .ttf file
    already placed in the provider's fonts/ directory and generates
    glyphmap.json from it. If no font is found, prints guidance.
    """
    from pathlib import Path

    pkg_root = Path(__file__).resolve().parents[1]
    fonts_dir = pkg_root / "fonts"
    ttfs = list(fonts_dir.glob("*.ttf")) if fonts_dir.exists() else []
    if not ttfs:
        print("No .ttf found in fonts/. Please supply a Simple Icons TTF via --font-file or place it under fonts/.")
        raise SystemExit(2)
    # Use the first discovered TTF
    return main(["--font-file", str(ttfs[0])])
