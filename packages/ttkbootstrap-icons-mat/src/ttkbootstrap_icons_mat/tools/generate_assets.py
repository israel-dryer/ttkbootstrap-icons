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
    # Material Design Icons (MDI) via jsdelivr
    # Note: This is MDI, not Google's Material Symbols.
    "mdi": {
        "version": "7.4.47",
        "url": "https://cdn.jsdelivr.net/npm/@mdi/font@{ver}/fonts/materialdesignicons-webfont.ttf",
    },
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Material Icons assets for ttkbootstrap-icons.")
    parser.add_argument("--font-url", help="URL to download the TTF font file")
    parser.add_argument("--font-file", help="Path to a local TTF font file")
    parser.add_argument("--map-url", help="URL to download official metadata JSON (optional)")
    parser.add_argument("--map-file", help="Path to local metadata JSON (optional)")
    parser.add_argument("--css-url", help="URL to a CSS file (optional); e.g., jsdelivr materialdesignicons.min.css")
    parser.add_argument("--css-file", help="Path to a local CSS file or directory (optional)")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()), help="Use a known CDN font URL preset")
    parser.add_argument("--version", help="Override preset version (e.g., 7.4.47)")
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    # Acquire font file
    font_path = None
    if args.font_file:
        font_path = Path(args.font_file)
    elif args.font_url:
        font_name = Path(args.font_url).name or "material.ttf"
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
    else:
        # Try CSS first for readable names
        css_text = None
        if args.css_file or args.css_url:
            src = args.css_file or args.css_url
            # If directory passed, pick materialdesignicons*.css inside
            if args.css_file and Path(src).exists() and Path(src).is_dir():
                cand = None
                for name in [
                    "materialdesignicons.min.css",
                    "materialdesignicons.css",
                ]:
                    p = Path(src) / name
                    if p.exists():
                        cand = str(p)
                        break
                if not cand:
                    for p in Path(src).glob("materialdesignicons*.css"):
                        cand = str(p)
                        break
                src = cand or src
            print(f"Using CSS: {src}")
            css_text = load_text(src)
        elif args.preset:
            ver = args.version or PRESETS[args.preset]["version"]
            css_url = f"https://cdn.jsdelivr.net/npm/@mdi/font@{ver}/css/materialdesignicons.min.css"
            try:
                print(f"Fetching CSS: {css_url}")
                css_text = load_text(css_url)
            except Exception:
                css_text = None
        if css_text:
            mapping = glyphmap_from_css(css_text, class_prefixes=("mdi-",))
            if mapping:
                sample = list(mapping.keys())[:10]
                print(f"Extracted {len(mapping)} names from CSS; sample: {sample}")
            else:
                print("CSS parsed but no icon mappings found; will attempt TTF cmap.")
    if not mapping:
        try:
            mapping = glyphmap_from_ttf(font_path)
        except Exception as e:
            raise SystemExit(
                "Failed to derive glyphmap from TTF and CSS. Provide a CSS file via --css-file or --css-url."
            ) from e

    write_glyphmap(pkg_root / "glyphmap.json", mapping)
    print(f"Wrote: {pkg_root / 'glyphmap.json'}")
    print(f"Font at: {font_path}")


if __name__ == "__main__":
    main()


def default_main():
    """Build using recommended defaults (mdi preset)."""
    return main(["--preset", "mdi"])
