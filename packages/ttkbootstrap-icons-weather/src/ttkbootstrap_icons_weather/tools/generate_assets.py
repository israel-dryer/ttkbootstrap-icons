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
    # Weather Icons via cdnjs
    "wi2": {
        "version": "2.0.10",
        "url": "https://cdnjs.cloudflare.com/ajax/libs/weather-icons/{ver}/font/weathericons-regular-webfont.ttf",
    },
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Weather Icons assets for ttkbootstrap-icons.")
    parser.add_argument("--font-url", help="URL to download the TTF font file")
    parser.add_argument("--font-file", help="Path to a local TTF font file")
    parser.add_argument("--map-url", help="URL to download official metadata JSON (optional)")
    parser.add_argument("--map-file", help="Path to local metadata JSON (optional)")
    parser.add_argument("--css-url", help="URL to a CSS file (optional)")
    parser.add_argument("--css-file", help="Path to a local CSS file or directory (optional)")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()), help="Use a known CDN font URL preset")
    parser.add_argument("--version", help="Override preset version (e.g., 2.0.10)")
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    # Acquire font file
    if args.font_file:
        font_path = Path(args.font_file)
    elif args.font_url:
        font_name = Path(args.font_url).name or "weather-icons.ttf"
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
        # Try to parse CSS for readable names
        css_texts = []
        if args.css_file or args.css_url:
            src = args.css_file or args.css_url
            # Directory support
            if args.css_file and Path(src).exists() and Path(src).is_dir():
                picks = []
                for name in [
                    "weather-icons.min.css",
                    "weather-icons.css",
                    "weather-icons-wind.min.css",
                    "weather-icons-wind.css",
                ]:
                    p = Path(src) / name
                    if p.exists():
                        picks.append(str(p))
                if not picks:
                    for p in Path(src).glob("weather-icons*.css"):
                        picks.append(str(p))
                for p in picks:
                    print(f"Using CSS: {p}")
                    css_texts.append(load_text(p))
            else:
                print(f"Using CSS: {src}")
                css_texts.append(load_text(src))
        elif args.preset:
            ver = args.version or PRESETS[args.preset]["version"]
            css_candidates = [
                f"https://cdnjs.cloudflare.com/ajax/libs/weather-icons/{ver}/css/weather-icons.min.css",
                f"https://cdnjs.cloudflare.com/ajax/libs/weather-icons/{ver}/css/weather-icons.css",
                f"https://cdnjs.cloudflare.com/ajax/libs/weather-icons/{ver}/css/weather-icons-wind.min.css",
                f"https://cdnjs.cloudflare.com/ajax/libs/weather-icons/{ver}/css/weather-icons-wind.css",
            ]
            for url in css_candidates:
                try:
                    print(f"Fetching CSS: {url}")
                    css_texts.append(load_text(url))
                except Exception:
                    continue
        if css_texts:
            combined = {}
            for css in css_texts:
                m = glyphmap_from_css(css, class_prefixes=("wi-",))
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
    """Build using recommended defaults (wi2 preset)."""
    return main(["--preset", "wi2"])
