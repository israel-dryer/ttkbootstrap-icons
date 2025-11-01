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


# Known upstream sources. You can override via CLI args.
PRESETS = {
    # Fontello Meteocons font repo (raw). Versions aren’t tagged; use main.
    # If this URL changes, point --font-url/--css-url to the new locations.
    "fontello": {
        "font_url": "https://raw.githubusercontent.com/fontello/meteocons.font/master/font/meteocons.ttf",
        "css_url": "https://raw.githubusercontent.com/fontello/meteocons.font/master/css/meteocons.css",
    },
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Meteocons assets for ttkbootstrap-icons.")
    parser.add_argument("--font-url", help="URL to download the TTF/OTF font file")
    parser.add_argument("--font-file", help="Path to a local TTF/OTF font file")
    parser.add_argument("--map-url", help="URL to download metadata JSON (optional)")
    parser.add_argument("--map-file", help="Path to local metadata JSON (optional)")
    parser.add_argument("--css-url", help="URL to a CSS file (optional)")
    parser.add_argument("--css-file", help="Path to a local CSS file or directory (optional)")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()), help="Use a known upstream preset")
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    # Acquire font file
    if args.font_file:
        # Copy local font into package fonts dir for packaging
        src_font = Path(args.font_file)
        if not src_font.exists():
            raise SystemExit(f"Font file not found: {src_font}")
        dest_name = src_font.name
        font_path = fonts_dir / dest_name
        if font_path.resolve() != src_font.resolve():
            # Copy bytes into package fonts directory
            font_path.write_bytes(src_font.read_bytes())
    elif args.font_url:
        font_name = Path(args.font_url).name or "meteocons.ttf"
        font_path = fonts_dir / font_name
        download_to(args.font_url, font_path)
    elif args.preset:
        preset = PRESETS[args.preset]
        font_url = preset.get("font_url")
        if not font_url:
            raise SystemExit("Preset missing font_url; specify --font-url instead.")
        font_name = Path(font_url).name
        font_path = fonts_dir / font_name
        download_to(font_url, font_path)
    else:
        raise SystemExit("--font-url or --font-file or --preset is required")

    # Build glyphmap
    mapping = None

    # Prefer provided metadata (if available)
    if args.map_file or args.map_url:
        data = load_json(args.map_file or args.map_url)
        mapping = glyphmap_from_metadata(data)
    else:
        # Try to parse CSS for readable names
        css_texts = []
        css_src = args.css_file or args.css_url
        if not css_src and args.preset:
            css_src = PRESETS[args.preset].get("css_url")
        if css_src:
            if args.css_file and Path(css_src).exists() and Path(css_src).is_dir():
                # If directory given, pick common filenames
                picks = []
                for name in ["meteocons.css", "meteocons.min.css", "meteocons-font.css"]:
                    p = Path(css_src) / name
                    if p.exists():
                        picks.append(str(p))
                if not picks:
                    for p in Path(css_src).glob("*.css"):
                        picks.append(str(p))
                for p in picks:
                    print(f"Using CSS: {p}")
                    css_texts.append(load_text(p))
            else:
                print(f"Using CSS: {css_src}")
                css_texts.append(load_text(css_src))

        if css_texts:
            combined = {}
            # Meteocons CSS classes typically use `icon-` or vendor-specific prefixes.
            # We allow broad prefixes to capture class names, then strip the prefix.
            # Adjust if upstream naming differs.
            for css in css_texts:
                m = glyphmap_from_css(css, class_prefixes=("icon-", "meteocons-", "mc-"))
                combined.update(m)
            mapping = combined
            if mapping:
                sample = list(mapping.keys())[:10]
                print(f"Extracted {len(mapping)} names from CSS; sample: {sample}")
            else:
                print("CSS parsed but no icon mappings found; falling back to TTF cmap.")

    if not mapping:
        mapping = glyphmap_from_ttf(font_path)

    # Filter out whitespace or empty glyphs that can occur in some icon fonts
    mapping = _filter_blank_glyphs(font_path, mapping)

    write_glyphmap(pkg_root / "glyphmap.json", mapping)
    print(f"Wrote: {pkg_root / 'glyphmap.json'}")
    print(f"Font at: {font_path}")


def default_main():
    """Build using the fontello upstream preset."""
    return main(["--preset", "fontello"])


def _filter_blank_glyphs(font_path: Path, mapping: dict[str, int]) -> dict[str, int]:
    """Remove entries that map to whitespace or empty glyphs.

    Heuristics:
    - Drop control/whitespace codepoints (isspace or < 0x20)
    - If 'glyf' table present, drop glyphs with zero contours (not composites)
    - Drop obvious placeholder glyph names (space/.notdef/uni0000)
    """
    try:
        from fontTools.ttLib import TTFont  # type: ignore
    except Exception:
        # If fontTools not available, do a basic unicode filter only
        return {
            name: cp
            for name, cp in mapping.items()
            if cp >= 32 and not chr(cp).isspace() and name not in {"space", ".notdef", "uni0000", "u0000"}
        }
    try:
        font = TTFont(str(font_path))
        glyf = font.get("glyf")
        cmap_table = None
        for table in font["cmap"].tables:
            if table.isUnicode():
                cmap_table = table.cmap
                break
        if cmap_table is None:
            # fallback to simple filtering
            return {
                name: cp
                for name, cp in mapping.items()
                if cp >= 32 and not chr(cp).isspace() and name not in {"space", ".notdef", "uni0000", "u0000"}
            }

        def is_blank_glyph(gn: str) -> bool:
            if not glyf or gn not in glyf.keys():
                return False
            g = glyf[gn]
            # numberOfContours == 0 => empty; == -1 => composite (usually not blank)
            try:
                return getattr(g, "numberOfContours", 1) == 0
            except Exception:
                return False

        filtered: dict[str, int] = {}
        for name, cp in mapping.items():
            if cp < 32 or chr(cp).isspace():
                continue
            if name in {"space", ".notdef", "uni0000", "u0000"}:
                continue
            gn = cmap_table.get(cp)
            if gn and is_blank_glyph(gn):
                continue
            filtered[name] = cp
        return filtered
    except Exception:
        # On any failure, return mapping with basic unicode filtering
        return {
            name: cp
            for name, cp in mapping.items()
            if cp >= 32 and not chr(cp).isspace() and name not in {"space", ".notdef", "uni0000", "u0000"}
        }


if __name__ == "__main__":
    main()
