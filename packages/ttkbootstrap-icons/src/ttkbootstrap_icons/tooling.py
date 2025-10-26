"""Utility helpers for downloading fonts and generating glyph maps.

These are developer tools intended to help populate provider packages with
font assets (TTF files) and a glyphmap.json that maps icon names to unicode
codepoints. They are not used at runtime by the icon renderer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, Tuple


def download_to(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as resp:  # nosec - executed by developer
        data = resp.read()
    dest.write_bytes(data)


def load_json(source: str) -> dict | list:
    p = Path(source)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    with urllib.request.urlopen(source) as resp:  # nosec - executed by developer
        return json.load(resp)


def normalize_codepoint(value) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        s = value.strip().lstrip("\\").lstrip("U+").lstrip("0x").strip()
        return int(s, 16)
    raise ValueError(f"Unsupported codepoint type: {type(value)}")


def glyphmap_from_metadata(data: dict | list) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    if isinstance(data, dict):
        # Either {name: hex} or {name: {encodedCode|unicode: code}}
        sample = next(iter(data.values())) if data else None
        if isinstance(sample, dict):
            for name, meta in data.items():
                code = meta.get("encodedCode") or meta.get("unicode") or meta.get("codepoint")
                if not code:
                    continue
                try:
                    mapping[name] = normalize_codepoint(code)
                except Exception:
                    continue
        else:
            for name, code in data.items():
                try:
                    mapping[name] = normalize_codepoint(code)
                except Exception:
                    continue
        return mapping
    elif isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            code = item.get("encodedCode") or item.get("unicode") or item.get("codepoint")
            if not name or not code:
                continue
            try:
                mapping[name] = normalize_codepoint(code)
            except Exception:
                continue
        return mapping
    else:
        raise ValueError("Unsupported metadata JSON format")


def glyphmap_from_ttf(ttf_path: Path) -> Dict[str, int]:
    try:
        from fontTools.ttLib import TTFont  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "fontTools is required to derive glyph maps from TTF. Install with 'pip install fonttools'."
        ) from e

    font = TTFont(str(ttf_path))
    cmap = None
    # Pick the best unicode cmap
    for table in font["cmap"].tables:
        if table.isUnicode():
            cmap = table.cmap
            break
    if cmap is None:
        raise RuntimeError("No Unicode cmap found in font")

    mapping: Dict[str, int] = {}
    for codepoint, glyphname in cmap.items():
        # Create a human-readable name from glyph name when possible
        name = glyphname
        # e.g., 'uniF101' -> '' (we'd rather skip unnamed glyphs)
        m = re.fullmatch(r"uni([0-9A-Fa-f]{4,6})", glyphname)
        if m:
            # Without vendor metadata, names may be poor quality; keep hex as fallback
            # but still include them so the set is usable.
            name = f"u{m.group(1).lower()}"
        name = name.replace(".", "-").replace("_", "-").lower()
        mapping[name] = int(codepoint)

    if not mapping:
        raise RuntimeError("No glyphs found in font cmap")
    return mapping


def write_glyphmap(path: Path, mapping: Dict[str, int]) -> None:
    # Write as a flat dict of name -> hex codepoint string
    data = {name: f"{code:04x}" for name, code in sorted(mapping.items())}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

