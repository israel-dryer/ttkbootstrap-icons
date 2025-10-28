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


PRESETS = {
    # RPG Awesome via cdnjs and GitHub raw (fallbacks)
    "rpga": {
        "version": "0.2.0",
        # Prioritize GitHub raw (source of truth), then CDN fallbacks
        "font_candidates": [
            "https://raw.githubusercontent.com/nagoshiashumari/Rpg-Awesome/master/fonts/rpgawesome-webfont.ttf",
            "https://cdnjs.cloudflare.com/ajax/libs/rpg-awesome/{ver}/fonts/rpgawesome-webfont.ttf",
        ],
        "css_candidates": [
            "https://raw.githubusercontent.com/nagoshiashumari/Rpg-Awesome/master/css/rpg-awesome.css",
            "https://cdnjs.cloudflare.com/ajax/libs/rpg-awesome/{ver}/css/rpg-awesome.css",
            "https://cdnjs.cloudflare.com/ajax/libs/rpg-awesome/{ver}/css/rpg-awesome.min.css",
        ],
    }
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate RPG Awesome assets for ttkbootstrap-icons.")
    parser.add_argument("--font-url", help="URL to download the TTF font file")
    parser.add_argument("--font-file", help="Path to a local TTF font file")
    parser.add_argument("--css-url", help="URL to a CSS file mapping (optional)")
    parser.add_argument("--css-file", help="Path to a local CSS file (optional)")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()), help="Use a known source preset")
    parser.add_argument("--version", help="Override preset version (e.g., 0.2.0)")
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    # Acquire font file (try multiple candidates when using preset)
    if args.font_file:
        font_path = Path(args.font_file)
    elif args.font_url:
        font_name = Path(args.font_url).name or "rpgawesome-webfont.ttf"
        font_path = fonts_dir / font_name
        download_to(args.font_url, font_path)
    elif args.preset:
        ver = args.version or PRESETS[args.preset]["version"]
        last_err = None
        font_path = None
        for url in PRESETS[args.preset]["font_candidates"]:
            try:
                url = url.format(ver=ver)
                target = fonts_dir / Path(url).name
                download_to(url, target)
                font_path = target
                break
            except Exception as e:
                last_err = e
                continue
        if font_path is None:
            raise SystemExit(f"Failed to download RPG Awesome font; last error: {last_err}")
    else:
        raise SystemExit("--font-url or --font-file is required")

    # Build glyphmap using CSS if available
    mapping = None
    css_sources = []
    if args.css_file or args.css_url:
        css_sources = [args.css_file or args.css_url]
    elif args.preset:
        ver = args.version or PRESETS[args.preset]["version"]
        css_sources = [u.format(ver=ver) for u in PRESETS[args.preset]["css_candidates"]]
    for src in css_sources:
        try:
            css_text = load_text(str(src))
            # Guard against HTML responses (e.g., GitHub rate limits or 404 pages)
            probe = css_text.lstrip()[:200].lower()
            if probe.startswith("<") and ("<html" in probe or "<!doctype" in probe):
                print(f"Warning: CSS at {src} looks like HTML; skipping")
                continue
            mapping = glyphmap_from_css(css_text, class_prefixes=("ra-",))
            if mapping:
                sample = list(mapping.keys())[:10]
                print(f"Extracted {len(mapping)} names from CSS; sample: {sample}")
                break
            # Retry by normalizing combined class selectors like .ra.ra-sword:before -> .ra-sword:before
            import re as _re
            css_norm = _re.sub(r"\.ra\s*\.(ra-[a-z0-9\-]+)", r".\1", css_text, flags=_re.IGNORECASE)
            if css_norm != css_text:
                mapping = glyphmap_from_css(css_norm, class_prefixes=("ra-",))
                if mapping:
                    sample = list(mapping.keys())[:10]
                    print(f"Extracted {len(mapping)} names from normalized CSS; sample: {sample}")
                    break
        except Exception as e:
            print(f"Warning: CSS parse failed from {src} ({e})")

    if not mapping:
        mapping = glyphmap_from_ttf(font_path)

    write_glyphmap(pkg_root / "glyphmap.json", mapping)
    print(f"Wrote: {pkg_root / 'glyphmap.json'}")
    print(f"Font at: {font_path}")


if __name__ == "__main__":
    main()


def default_main():
    return main(["--preset", "rpga"])
