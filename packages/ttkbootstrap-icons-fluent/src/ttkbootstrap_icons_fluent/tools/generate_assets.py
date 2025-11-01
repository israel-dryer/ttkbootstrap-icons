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
from urllib.error import HTTPError, URLError

"""
    TODO automate the normalization
    - strip prefix
    - strip sizes
    - use first instance of each item with same key
"""

PRESETS = {
    # Microsoft Fluent System Icons from GitHub releases
    "fluent-regular": {
        "version": "1.1.261",
        # Distribute as a zip; we'll extract the TTF
        "url": "https://github.com/microsoft/fluentui-system-icons/releases/download/v{ver}/FluentSystemIcons-Font.zip",
    },
    "fluent-filled": {
        "version": "1.1.261",
        # Same zip contains both regular and filled fonts
        "url": "https://github.com/microsoft/fluentui-system-icons/releases/download/v{ver}/FluentSystemIcons-Font.zip",
    },
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Fluent System Icons assets for ttkbootstrap-icons.")
    parser.add_argument("--font-url", help="URL to download the TTF font file")
    parser.add_argument("--font-file", help="Path to a local TTF font file")
    parser.add_argument("--map-url", help="URL to download official metadata JSON (optional)")
    parser.add_argument("--map-file", help="Path to local metadata JSON (optional)")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--out-map", help="Output glyphmap filename (default: glyphmap.json)")
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()), help="Use a known release font URL preset")
    parser.add_argument("--version", help="Override preset version (e.g., 1.1.261)")
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    # Acquire font file
    if args.font_file:
        font_path = Path(args.font_file)
    elif args.font_url:
        url = args.font_url
        fname = Path(url).name
        if fname.lower().endswith(".zip"):
            # Download and extract zip
            import tempfile
            import zipfile

            with tempfile.TemporaryDirectory() as td:
                tmp_zip = Path(td) / fname
                download_to(url, tmp_zip)
                with zipfile.ZipFile(tmp_zip, "r") as zf:
                    # Extract TTFs
                    ttf_members = [m for m in zf.namelist() if m.lower().endswith(".ttf")]
                    if not ttf_members:
                        raise SystemExit("Zip did not contain any .ttf files")
                    zf.extractall(fonts_dir)
                    # Pick regular by default
                    preferred = [m for m in ttf_members if "regular" in m.lower()]
                    chosen = preferred[0] if preferred else ttf_members[0]
            font_path = fonts_dir / Path(chosen).name
        else:
            font_name = fname or "fluent-icons.ttf"
            font_path = fonts_dir / font_name
            download_to(url, font_path)
    elif args.preset:
        preset = PRESETS[args.preset]
        ver = args.version or preset["version"]
        # Try a series of known URLs
        # 1) GitHub releases (zip and direct TTFs)
        candidates = [
            preset["url"].format(ver=ver),
            f"https://github.com/microsoft/fluentui-system-icons/releases/download/{ver}/FluentSystemIcons-Font.zip",
            f"https://github.com/microsoft/fluentui-system-icons/releases/download/v{ver}/FluentSystemIcons-Font.zip",
        ]
        # Prefer specific TTF first depending on preset
        if args.preset == "fluent-regular":
            candidates += [
                f"https://github.com/microsoft/fluentui-system-icons/releases/download/{ver}/FluentSystemIcons-Regular.ttf",
                f"https://github.com/microsoft/fluentui-system-icons/releases/download/v{ver}/FluentSystemIcons-Regular.ttf",
            ]
        else:
            candidates += [
                f"https://github.com/microsoft/fluentui-system-icons/releases/download/{ver}/FluentSystemIcons-Filled.ttf",
                f"https://github.com/microsoft/fluentui-system-icons/releases/download/v{ver}/FluentSystemIcons-Filled.ttf",
            ]
        candidates += [
            "https://github.com/microsoft/fluentui-system-icons/releases/latest/download/FluentSystemIcons-Font.zip",
        ]
        # 2) Raw content from repository tags and main branch
        # Try different tag naming conventions
        tag_variants = [ver, f"v{ver}", f"fluentui-system-icons-{ver}"]
        ttf_name = (
            "FluentSystemIcons-Regular.ttf"
            if args.preset == "fluent-regular"
            else "FluentSystemIcons-Filled.ttf"
        )
        for tag in tag_variants:
            candidates.append(
                f"https://raw.githubusercontent.com/microsoft/fluentui-system-icons/{tag}/fonts/{ttf_name}"
            )
        # Fall back to main branch
        candidates.append(
            f"https://raw.githubusercontent.com/microsoft/fluentui-system-icons/main/fonts/{ttf_name}"
        )

        last_err = None
        for url in candidates:
            try:
                fname = Path(url).name
                if fname.lower().endswith(".zip"):
                    import tempfile
                    import zipfile

                    with tempfile.TemporaryDirectory() as td:
                        tmp_zip = Path(td) / fname
                        download_to(url, tmp_zip)
                        with zipfile.ZipFile(tmp_zip, "r") as zf:
                            ttf_members = [m for m in zf.namelist() if m.lower().endswith(".ttf")]
                            if not ttf_members:
                                raise SystemExit("Zip did not contain any .ttf files")
                            zf.extractall(fonts_dir)
                            preferred = [m for m in ttf_members if "regular" in m.lower() and args.preset == "fluent-regular"]
                            if args.preset == "fluent-filled":
                                preferred = [m for m in ttf_members if "filled" in m.lower()]
                            chosen = preferred[0] if preferred else ttf_members[0]
                            font_path = fonts_dir / Path(chosen).name
                            break
                else:
                    font_name = fname
                    font_path = fonts_dir / font_name
                    download_to(url, font_path)
                    break
            except (HTTPError, URLError) as e:
                last_err = e
                continue
        else:
            attempted = "\n - " + "\n - ".join(candidates)
            raise SystemExit(
                "Failed to download Fluent font from known URLs.\n"
                f"Last error: {last_err}\n"
                f"Attempted:{attempted}\n"
                "Please download the font zip from the official releases page and re-run with --font-file, e.g.:\n"
                "  ttkicons-fluent-build --font-file C:\\path\\to\\FluentSystemIcons-Regular.ttf"
            )
    else:
        raise SystemExit("--font-url or --font-file is required")

    # Build glyphmap
    if args.map_file or args.map_url:
        data = load_json(args.map_file or args.map_url)
        mapping = glyphmap_from_metadata(data)
    else:
        mapping = glyphmap_from_ttf(font_path)

    out_map = args.out_map or "glyphmap.json"
    write_glyphmap(pkg_root / out_map, mapping)
    print(f"Wrote: {pkg_root / out_map}")
    print(f"Font at: {font_path}")


if __name__ == "__main__":
    main()


def default_main():
    """Build recommended Fluent fonts: Regular, Filled, and try Light.

    This runs the builder multiple times:
    - Regular via preset
    - Filled via preset
    - Light via raw main URL (if available; skipped on 404)
    """
    # Regular
    try:
        main(["--preset", "fluent-regular", "--out-map", "glyphmap-regular.json"])
    except SystemExit:
        pass
    # Filled
    try:
        main(["--preset", "fluent-filled", "--out-map", "glyphmap-filled.json"])
    except SystemExit:
        pass
    # Light (best-effort; may not exist)
    try:
        main([
            "--font-url",
            "https://raw.githubusercontent.com/microsoft/fluentui-system-icons/main/fonts/FluentSystemIcons-Light.ttf",
            "--out-map",
            "glyphmap-light.json",
        ])
    except SystemExit:
        print("Light style not available; skipped")
