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
    # Typicons v2 assets are hosted in the upstream repo releases and various CDNs.
    # Provide a reasonable default for quick builds when network is available.
    "gh": {
        "css": "https://raw.githubusercontent.com/stephenhutchings/typicons.font/master/src/font/typicons.css",
        "ttf": "https://raw.githubusercontent.com/stephenhutchings/typicons.font/master/src/font/typicons.ttf",
    },
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Typicons assets for ttkbootstrap-icons.")
    parser.add_argument("--font-url", help="URL to download the TTF font file")
    parser.add_argument("--font-file", help="Path to a local TTF font file")
    parser.add_argument("--map-url", help="URL to download official metadata JSON (optional)")
    parser.add_argument("--map-file", help="Path to local metadata JSON (optional)")
    parser.add_argument("--css-url", help="URL to a CSS file (optional)")
    parser.add_argument("--css-file", help="Path to a local CSS file or directory (optional)")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()), help="Use a known URL preset (downloads CSS and TTF)")
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    # Acquire font file
    if args.font_file:
        font_path = Path(args.font_file)
    elif args.font_url:
        font_name = Path(args.font_url).name or "typicons.ttf"
        font_path = fonts_dir / font_name
        download_to(args.font_url, font_path)
    elif args.preset:
        url = PRESETS[args.preset]["ttf"]
        font_name = Path(url).name or "typicons.ttf"
        font_path = fonts_dir / font_name
        download_to(url, font_path)
    else:
        raise SystemExit("--font-url or --font-file is required (or use --preset gh)")

    # Build glyphmap
    mapping = None
    if args.map_file or args.map_url:
        data = load_json(args.map_file or args.map_url)
        mapping = glyphmap_from_metadata(data)
    else:
        # Try to parse CSS for readable names
        css_texts = []
        if args.css_file or args.css_url:
            src = args.css_file or args.css_url
            if args.css_file and Path(src).exists() and Path(src).is_dir():
                picks = []
                for name in [
                    "typicons.css",
                    "typicons.min.css",
                ]:
                    p = Path(src) / name
                    if p.exists():
                        picks.append(str(p))
                if not picks:
                    for p in Path(src).glob("typicons*.css"):
                        picks.append(str(p))
                for p in picks:
                    print(f"Using CSS: {p}")
                    css_texts.append(load_text(p))
            else:
                print(f"Using CSS: {src}")
                css_texts.append(load_text(src))
        elif args.preset:
            url = PRESETS[args.preset]["css"]
            try:
                print(f"Fetching CSS: {url}")
                css_texts.append(load_text(url))
            except Exception:
                pass
        if css_texts:
            combined = {}
            for css in css_texts:
                m = glyphmap_from_css(css, class_prefixes=("typcn-",))
                combined.update(m)
            mapping = combined
            if mapping:
                sample = list(mapping.keys())[:10]
                print(f"Extracted {len(mapping)} names from CSS; sample: {sample}")
            else:
                print("CSS parsed but no icon mappings found; falling back to TTF cmap.")
    if not mapping:
        mapping = glyphmap_from_ttf(font_path)

    write_glyphmap(pkg_root / "glyphmap.json", mapping)
    print(f"Wrote: {pkg_root / 'glyphmap.json'}")
    print(f"Font at: {font_path}")


if __name__ == "__main__":
    main()


def default_main():
    """Build using the GitHub raw preset (when network is available)."""
    return main(["--preset", "gh"])

