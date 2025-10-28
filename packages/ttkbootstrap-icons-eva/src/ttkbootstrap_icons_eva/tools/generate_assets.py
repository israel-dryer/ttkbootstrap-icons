from __future__ import annotations

import argparse
from pathlib import Path

from ttkbootstrap_icons.tooling import (
    download_to,
    load_text,
    glyphmap_from_ttf,
    glyphmap_from_css,
    write_glyphmap,
    ensure_dir,
)
from urllib.parse import urljoin
import re


PRESETS = {
    # Eva Icons from popular CDNs and GitHub raw (fallbacks tried in order)
    "eva": {
        "font_candidates": [
            "https://unpkg.com/eva-icons@latest/fonts/eva-icons.ttf",
            "https://unpkg.com/eva-icons/fonts/eva-icons.ttf",
            "https://unpkg.com/eva-icons@latest/style/fonts/eva-icons.ttf",
            "https://unpkg.com/eva-icons/style/fonts/eva-icons.ttf",
            "https://cdn.jsdelivr.net/npm/eva-icons/fonts/eva-icons.ttf",
            "https://cdn.jsdelivr.net/npm/eva-icons/style/fonts/eva-icons.ttf",
            "https://raw.githubusercontent.com/akveo/eva-icons/master/fonts/eva-icons.ttf",
            "https://raw.githubusercontent.com/akveo/eva-icons/master/style/fonts/eva-icons.ttf",
            "https://raw.githubusercontent.com/akveo/eva-icons/master/src/assets/fonts/eva-icons.ttf",
            "https://raw.githubusercontent.com/akveo/eva-icons/master/src/assets/fonts/Eva-Icons.ttf",
        ],
        "css_candidates": [
            "https://unpkg.com/eva-icons@latest/style/eva-icons.css",
            "https://unpkg.com/eva-icons/style/eva-icons.css",
            "https://cdn.jsdelivr.net/npm/eva-icons/style/eva-icons.css",
            "https://raw.githubusercontent.com/akveo/eva-icons/master/style/eva-icons.css",
            "https://raw.githubusercontent.com/akveo/eva-icons/master/src/style/eva-icons.css",
            "https://raw.githubusercontent.com/akveo/eva-icons/master/src/styles/eva-icons.css",
        ],
    }
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Eva Icons assets for ttkbootstrap-icons.")
    parser.add_argument("--font-url", help="URL to download the TTF font file")
    parser.add_argument("--font-file", help="Path to a local TTF font file")
    parser.add_argument("--css-url", help="URL to a CSS file mapping (optional)")
    parser.add_argument("--css-file", help="Path to a local CSS file (optional)")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()), help="Use a known source preset")
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    # Acquire font file (prefer discovering from CSS when using preset)
    if args.font_file:
        font_path = Path(args.font_file)
    elif args.font_url:
        font_name = Path(args.font_url).name or "eva-icons.ttf"
        font_path = fonts_dir / font_name
        download_to(args.font_url, font_path)
    elif args.preset:
        font_path = fonts_dir / "eva-icons.ttf"
        last_err = None
        # Try to discover font URL from CSS first
        discovered_urls = []
        for css_source in PRESETS[args.preset]["css_candidates"]:
            try:
                css_text = load_text(str(css_source))
                # Look for eva-icons.ttf in @font-face src URLs
                for m in re.finditer(r"url\(([^)]+\.ttf[^)]*)\)", css_text, flags=re.IGNORECASE):
                    raw = m.group(1).strip().strip('\"').strip("'")
                    # Resolve relative URLs against the CSS URL
                    abs_url = urljoin(css_source, raw)
                    if abs_url not in discovered_urls:
                        discovered_urls.append(abs_url)
                if discovered_urls:
                    break
            except Exception:
                continue
        # Try discovered URLs first (download all discovered TTFs when possible)
        any_ok = False
        for url in discovered_urls:
            try:
                target = fonts_dir / Path(url).name
                download_to(url, target)
                any_ok = True
            except Exception as e:
                last_err = e
                continue
        # Also try known candidates for primary font
        for url in PRESETS[args.preset]["font_candidates"]:
            try:
                target = fonts_dir / Path(url).name
                download_to(url, target)
                any_ok = True
            except Exception as e:
                last_err = e
                continue
        if not any_ok and last_err is not None:
            raise SystemExit(f"Failed to download Eva font from known URLs. Last error: {last_err}")
    else:
        raise SystemExit("--font-url or --font-file is required")

    # Build glyphmap using CSS if available for better names
    mapping = None
    css_candidates = []
    if args.css_file or args.css_url:
        css_candidates = [args.css_file or args.css_url]
    elif args.preset:
        css_candidates = PRESETS[args.preset]["css_candidates"]
    for css_source in css_candidates:
        try:
            css_text = load_text(str(css_source))
            # Eva uses class names like .eva-activity-outline or .eva-activity-fill
            mapping = glyphmap_from_css(css_text, class_prefixes=("eva-",))
            if mapping:
                sample = list(mapping.keys())[:10]
                print(f"Extracted {len(mapping)} names from CSS; sample: {sample}")
                break
        except Exception as e:
            print(f"Warning: CSS parse failed from {css_source} ({e})")

    if not mapping:
        mapping = glyphmap_from_ttf(font_path)

    # Write a single combined glyphmap
    write_glyphmap(pkg_root / "glyphmap.json", mapping)
    print(f"Wrote: {pkg_root / 'glyphmap.json'}")
    print(f"Font at: {font_path}")


if __name__ == "__main__":
    main()


def default_main():
    return main(["--preset", "eva"])
