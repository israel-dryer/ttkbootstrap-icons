from __future__ import annotations

import argparse
from pathlib import Path

from tkinter_icons.tools.tooling import (
    download_to,
    load_text,
    glyphmap_from_ttf,
    report_dropped,
    restrict_to_font,
    write_glyphmap,
    ensure_dir,
)


def parse_codepoints_text(text: str) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # format: name codepointHex
        parts = line.split()
        if len(parts) != 2:
            continue
        name, hexcp = parts
        try:
            mapping[name] = int(hexcp, 16)
        except Exception:
            continue
    return mapping


PRESETS = {
    "gmi": {"version": "latest"},
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Google Material Icons assets for tkinter-icons.")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()))
    parser.add_argument("--version", help="Version tag (or 'latest')", default="latest")
    # Allow custom sources
    parser.add_argument("--baseline-font-url", help="URL to baseline TTF")
    parser.add_argument("--outlined-font-url", help="URL to outlined OTF/TTF")
    parser.add_argument("--round-font-url", help="URL to round OTF/TTF")
    parser.add_argument("--sharp-font-url", help="URL to sharp OTF/TTF")
    parser.add_argument("--twotone-font-url", help="URL to twotone OTF/TTF")
    parser.add_argument("--codepoints-url", help="URL to baseline codepoints text")
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    ver = args.version

    def dl(urls: list[str], dest_name: str) -> Path | None:
        last_err = None
        dest = fonts_dir / dest_name
        for url in urls:
            try:
                download_to(url, dest)
                return dest
            except Exception as e:
                last_err = e
                continue
        return None

    # Candidate URLs for fonts and codepoints
    # Use Google Fonts CDN (fonts.gstatic.com) - these are the official webfont versions
    base_candidates = [
        f"https://fonts.gstatic.com/s/materialicons/v145/flUhRq6tzZclQEJ-Vdg-IuiaDsNZ.ttf",
        f"https://raw.githubusercontent.com/google/material-design-icons/master/font/MaterialIcons-Regular.ttf",
    ]
    outlined_candidates = [
        f"https://fonts.gstatic.com/s/materialiconsoutlined/v110/gok-H7zzDkdnRel8-DQ6KAXJ69wP1tGnf4ZGhUcd.otf",
        f"https://raw.githubusercontent.com/google/material-design-icons/master/font/MaterialIconsOutlined-Regular.otf",
    ]
    round_candidates = [
        f"https://fonts.gstatic.com/s/materialiconsround/v109/LDItaoyNOAY6Uewc665JcIzCKsKc_M9flwmJ.otf",
        f"https://raw.githubusercontent.com/google/material-design-icons/master/font/MaterialIconsRound-Regular.otf",
    ]
    sharp_candidates = [
        f"https://fonts.gstatic.com/s/materialiconssharp/v110/oPWQ_lt5nv4pWNJpghLP75WiFR4kLh3kvmvR.otf",
        f"https://raw.githubusercontent.com/google/material-design-icons/master/font/MaterialIconsSharp-Regular.otf",
    ]
    twotone_candidates = [
        f"https://fonts.gstatic.com/s/materialiconstwotone/v111/hESh6WRmNCxEqUmNyh3JDeGxjVVyMg4tHGctNCu3.otf",
        f"https://raw.githubusercontent.com/google/material-design-icons/master/font/MaterialIconsTwoTone-Regular.otf",
    ]
    codepoints_candidates = [
        f"https://raw.githubusercontent.com/google/material-design-icons/master/font/MaterialIcons-Regular.codepoints",
        f"https://raw.githubusercontent.com/google/material-design-icons/master/iconfont/codepoints",
    ]

    # Override with custom URLs when provided
    if args.baseline_font_url:
        base_candidates = [args.baseline_font_url]
    if args.outlined_font_url:
        outlined_candidates = [args.outlined_font_url]
    if args.round_font_url:
        round_candidates = [args.round_font_url]
    if args.sharp_font_url:
        sharp_candidates = [args.sharp_font_url]
    if args.twotone_font_url:
        twotone_candidates = [args.twotone_font_url]
    if args.codepoints_url:
        codepoints_candidates = [args.codepoints_url]

    # Download
    base_font = dl(base_candidates, "MaterialIcons-Regular.ttf")
    outlined_font = dl(outlined_candidates, "MaterialIconsOutlined-Regular.otf")
    round_font = dl(round_candidates, "MaterialIconsRound-Regular.otf")
    sharp_font = dl(sharp_candidates, "MaterialIconsSharp-Regular.otf")
    twotone_font = dl(twotone_candidates, "MaterialIconsTwoTone-Regular.otf")

    # Build glyphmap from codepoints
    codepoints_text = None
    for url in codepoints_candidates:
        try:
            codepoints_text = load_text(url)
            break
        except Exception:
            continue
    if not codepoints_text:
        raise SystemExit("Failed to download Material Icons codepoints mapping.")
    mapping = parse_codepoints_text(codepoints_text)
    if not mapping:
        raise SystemExit("Parsed codepoints mapping is empty.")

    # Write a separate glyphmap for each style, restricted to what that style's
    # own font actually carries.
    #
    # This used to write `mapping` verbatim to all four, under a comment saying
    # Material Icons use the same codepoints across all styles. They do not. The
    # codepoints file downloaded above is the *baseline* one, and baseline
    # carries 43 codepoints `outlined` lacks, 38 `round` lacks, and 38 `sharp`
    # lacks. All four styles reporting an identical name count was the visible
    # symptom; 119 names that drew an empty square with no error was the cost
    # (#140). Each style is now checked against the font it will be drawn from.
    style_fonts = {
        "baseline": base_font,
        "outlined": outlined_font,
        "round": round_font,
        "sharp": sharp_font,
    }
    # Every font is checked before anything is written. Refusing partway through
    # would leave the styles already written regenerated beside the rest stale,
    # which is a worse tree than the one this started with — and the download
    # most likely to fail is the last one attempted as readily as the first.
    undownloaded = [style for style, font_path in style_fonts.items() if font_path is None]
    if undownloaded:
        raise SystemExit(
            f"The {', '.join(undownloaded)} font(s) were not downloaded, so their glyph maps "
            f"cannot be checked against them. Refusing to write any glyph map, since a glyph "
            f"map that advertises glyphs its font does not carry is what this guards against."
        )

    print("\nChecking each style's names against its own font:")
    for style, font_path in style_fonts.items():
        style_mapping, dropped = restrict_to_font(mapping, font_path)
        report_dropped(style, dropped)
        glyphmap_path = pkg_root / f"glyphmap-{style}.json"
        write_glyphmap(glyphmap_path, style_mapping)
        print(f"Wrote: {glyphmap_path} ({len(style_mapping)} names)")

    print("\nDownloaded fonts:")
    for label, p in (
        ("baseline", base_font), ("outlined", outlined_font), ("round", round_font), ("sharp", sharp_font), ("twotone", twotone_font)
    ):
        if p:
            print(f"  {label}: {p}")
        else:
            print(f"  {label}: not downloaded")


if __name__ == "__main__":
    main()


def default_main():
    return main(["--preset", "gmi", "--version", "latest"])

