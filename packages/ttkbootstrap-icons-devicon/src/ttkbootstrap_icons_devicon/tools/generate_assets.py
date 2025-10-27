from __future__ import annotations

import argparse
from pathlib import Path

# Import developer tooling without pulling heavy runtime deps. We prefer importing
# the local repo's tooling module directly by path to avoid importing the
# ttkbootstrap_icons package __init__ (which pulls PIL).
try:
    from ttkbootstrap_icons.tooling import (  # type: ignore
        download_to,
        load_text,
        load_json,
        glyphmap_from_ttf,
        glyphmap_from_css,
        write_glyphmap,
        ensure_dir,
    )
except Exception:  # pragma: no cover - fallback path loader
    import importlib.util as _ilu
    import sys as _sys
    REPO_ROOT = Path(__file__).resolve().parents[5]
    TOOLING_PATH = REPO_ROOT / "packages" / "ttkbootstrap-icons" / "src" / "ttkbootstrap_icons" / "tooling.py"
    spec = _ilu.spec_from_file_location("_ttkicons_tooling", TOOLING_PATH)
    if spec and spec.loader:
        mod = _ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        download_to = mod.download_to
        load_text = mod.load_text
        load_json = mod.load_json
        glyphmap_from_ttf = mod.glyphmap_from_ttf
        glyphmap_from_css = mod.glyphmap_from_css
        write_glyphmap = mod.write_glyphmap
        ensure_dir = mod.ensure_dir
    else:
        raise RuntimeError("Unable to load ttkbootstrap_icons.tooling module")


PRESETS = {
    # Devicon upstream raw files
    "devicon": {
        "font_url": "https://raw.githubusercontent.com/devicons/devicon/master/fonts/devicon.ttf",
        # Note: CSS lives at repo root, not under fonts/
        "css_url": "https://raw.githubusercontent.com/devicons/devicon/master/devicon.min.css",
        "css_base_url": "https://raw.githubusercontent.com/devicons/devicon/master/devicon-base.css",
        "meta_url": "https://raw.githubusercontent.com/devicons/devicon/master/devicon.json",
    }
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Devicon assets for ttkbootstrap-icons.")
    parser.add_argument("--font-url", help="URL to download the TTF font file")
    parser.add_argument("--font-file", help="Path to a local TTF font file")
    parser.add_argument("--css-url", help="URL to a CSS file mapping (optional)")
    parser.add_argument("--css-file", help="Path to a local CSS file (optional)")
    parser.add_argument("--meta-url", help="URL to devicon.json metadata (optional)")
    parser.add_argument("--meta-file", help="Path to local devicon.json (optional)")
    parser.add_argument("--out-dir", help="Output package directory", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()), help="Use a known source preset")
    args = parser.parse_args(argv)

    pkg_root = Path(args.out_dir)
    fonts_dir = pkg_root / "fonts"
    ensure_dir(fonts_dir)

    # Acquire font file
    if args.font_file:
        font_path = Path(args.font_file)
    elif args.font_url:
        font_name = Path(args.font_url).name or "devicon.ttf"
        font_path = fonts_dir / font_name
        download_to(args.font_url, font_path)
    elif args.preset:
        url = PRESETS[args.preset]["font_url"]
        font_name = Path(url).name
        font_path = fonts_dir / font_name
        download_to(url, font_path)
    else:
        raise SystemExit("--font-url or --font-file is required")

    # Build glyphmap using CSS if available for better names
    mapping = None
    css_candidates = []
    if args.css_file or args.css_url:
        css_candidates = [args.css_file or args.css_url]
    elif args.preset:
        primary = PRESETS[args.preset]["css_url"]
        css_candidates = [primary]
        if primary.endswith(".min.css"):
            css_candidates.append(primary.replace(".min.css", ".css"))
        # Also try devicon-base.css which contains alias classes
        base_url = PRESETS[args.preset].get("css_base_url")
        if base_url:
            css_candidates.append(base_url)
    for css_source in css_candidates:
        try:
            css_text = load_text(str(css_source))
            mapping = glyphmap_from_css(css_text, class_prefixes=("devicon-",))
            if mapping:
                sample = list(mapping.keys())[:10]
                print(f"Extracted {len(mapping)} names from CSS; sample: {sample}")
                break
        except Exception as e:
            print(f"Warning: CSS parse failed from {css_source} ({e})")

    # If metadata available, constrain/normalize names to human-friendly forms
    meta_source = args.meta_file or args.meta_url or (args.preset and PRESETS[args.preset].get("meta_url")) or None
    if meta_source:
        try:
            meta = load_json(str(meta_source))
            desired_names = set()
            alias_pairs = {}  # name -> list[(base, alias)]
            # devicon.json is a list of records with fields like:
            # { "name": "python", "versions": { "font": ["plain", "plain-wordmark", ...] } }
            if isinstance(meta, list):
                for item in meta:
                    try:
                        base = item.get("name")
                        variants = (item.get("versions", {}) or {}).get("font", [])
                        aliases = item.get("aliases", []) or []
                        if base and isinstance(variants, list):
                            for v in variants:
                                desired_names.add(f"{base}-{v}")
                        if base and isinstance(aliases, list):
                            alias_pairs[base] = [(a.get("base"), a.get("alias")) for a in aliases if a.get("base") and a.get("alias")]
                    except Exception:
                        continue
            # Remap CSS-derived names to only include desired ones, if present
            if mapping:
                filtered = {}
                for k, cp in mapping.items():
                    # mapping includes both stripped and full class names
                    # Keep stripped form preferred; allow full class as alias
                    key = k
                    if k.startswith("devicon-"):
                        key = k[len("devicon-") :]
                    if key in desired_names:
                        filtered[key] = cp
                if filtered:
                    mapping = filtered
                # Expand alias variants if metadata defines them and base exists
                try:
                    to_add = {}
                    for name in list(mapping.keys()):
                        # name pattern: {base}-{variant}
                        if "-" not in name:
                            continue
                        base_name, variant = name.split("-", 1)
                        for b, alias in alias_pairs.get(base_name, []):
                            if variant == b and f"{base_name}-{alias}" not in mapping:
                                to_add[f"{base_name}-{alias}"] = mapping[name]
                    mapping.update(to_add)
                except Exception:
                    pass
        except Exception as e:
            print(f"Warning: metadata parse failed; continuing without meta normalization ({e})")

    if not mapping:
        mapping = glyphmap_from_ttf(font_path)

    # Add convenience aliases: if a 'name-plain' exists, also include 'name'
    try:
        to_add = {}
        for k, cp in list(mapping.items()):
            if k.endswith("-plain"):
                base = k[:-6]
                if base and base not in mapping:
                    to_add[base] = cp
        mapping.update(to_add)
    except Exception:
        pass

    write_glyphmap(pkg_root / "glyphmap.json", mapping)
    print(f"Wrote: {pkg_root / 'glyphmap.json'}")
    print(f"Font at: {font_path}")


if __name__ == "__main__":
    main()


def default_main():
    """Build using recommended defaults (Devicon preset)."""
    return main(["--preset", "devicon"])
