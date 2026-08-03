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


def load_text(source: str) -> str:
    p = Path(source)
    if p.exists():
        return p.read_text(encoding="utf-8")
    with urllib.request.urlopen(source) as resp:  # nosec - executed by developer
        return resp.read().decode("utf-8")


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


def glyphmap_from_css(css_text: str, class_prefixes: Iterable[str] = ("ion-ios-", "ion-md-", "ion-",)) -> Dict[str, int]:
    """Extract a glyph map from a CSS file with .class:before { content: "\fxxx" } rules.

    This is useful for icon fonts like Ionicons v2 which distribute names via CSS.
    """
    mapping: Dict[str, int] = {}
    # Build pattern for allowed prefixes
    prefix_pat = "|".join(re.escape(p) for p in class_prefixes)
    # Matches e.g.:
    # .ion-alert:before { content: "\f101"; }
    # .ion-alert::before{content:'\f101'}
    # Allow single or double quotes, one backslash before hex
    # Pattern 1: with quotes around a hexadecimal content value (e.g., "\f101")
    pattern1 = re.compile(
        rf"\.((?:{prefix_pat})[a-z0-9\-]+)::?before\s*\{{[^}}]*content\s*:\s*([\'\"])\\([0-9a-fA-F]+)\2",
        re.IGNORECASE | re.DOTALL,
    )
    # Pattern 2: sometimes minifiers may drop quotes (rare). Support without quotes.
    pattern2 = re.compile(
        rf"\.((?:{prefix_pat})[a-z0-9\-]+)::?before\s*\{{[^}}]*content\s*:\s*\\([0-9a-fA-F]+)",
        re.IGNORECASE | re.DOTALL,
    )
    # Pattern 3: quoted literal glyph (e.g., content: ""), common in some icon CSS
    pattern3 = re.compile(
        rf"\.((?:{prefix_pat})[a-z0-9\-]+)::?before\s*\{{[^}}]*content\s*:\s*([\'\"])(.)\2",
        re.IGNORECASE | re.DOTALL,
    )

    matches = list(pattern1.finditer(css_text))
    literal_matches = []
    if not matches:
        matches = list(pattern2.finditer(css_text))
        # Also collect literal glyph matches in a second pass
        literal_matches = list(pattern3.finditer(css_text))

    for m in matches:
        klass = m.group(1)
        hexcp = m.group(2) if m.lastindex and m.lastindex >= 2 else m.group(m.lastindex)
        # strip prefix to make shorter names (e.g., 'ion-alert' -> 'alert')
        name = klass
        for pref in class_prefixes:
            if name.startswith(pref):
                name = name[len(pref) :]
                break
        try:
            code = int(hexcp, 16)
            # Add both stripped and original class name for flexibility
            mapping[name] = code
            mapping[klass] = code
        except Exception:
            continue

    # Handle quoted literal glyphs (e.g., content: "")
    for m in literal_matches:
        klass = m.group(1)
        glyph = m.group(3)
        if not glyph:
            continue
        name = klass
        for pref in class_prefixes:
            if name.startswith(pref):
                name = name[len(pref) :]
                break
        try:
            code = ord(glyph)
            mapping[name] = code
            mapping[klass] = code
        except Exception:
            continue
    if mapping:
        return mapping

    # Fallback parser: iterate CSS blocks and handle comma-separated selectors
    block_re = re.compile(r"([^\{]+)\{([^\}]*)\}", re.DOTALL)
    cp_re_quoted = re.compile(r"content\s*:\s*([\'\"])\\([0-9a-fA-F]+)\1", re.IGNORECASE)
    cp_re_literal = re.compile(r"content\s*:\s*([\'\"])(.)\1", re.IGNORECASE | re.DOTALL)
    cp_re_unquoted = re.compile(r"content\s*:\s*\\([0-9a-fA-F]+)", re.IGNORECASE)
    sel_re = re.compile(rf"\.((?:{prefix_pat})[a-z0-9\-]+)::?before\s*$", re.IGNORECASE)

    for m in block_re.finditer(css_text):
        selectors = m.group(1)
        body = m.group(2)
        mcp = cp_re_quoted.search(body) or cp_re_unquoted.search(body) or cp_re_literal.search(body)
        if not mcp:
            continue
        # Determine codepoint value based on which capture matched
        hexcp = None
        literal_char = None
        if mcp.re is cp_re_literal:
            literal_char = mcp.group(2)
        else:
            hexcp = mcp.group(2)
        for sel in selectors.split(','):
            sel = sel.strip()
            ms = sel_re.search(sel)
            if not ms:
                continue
            klass = ms.group(1)
            name = klass
            for pref in class_prefixes:
                if name.startswith(pref):
                    name = name[len(pref) :]
                    break
            try:
                if literal_char is not None and len(literal_char) >= 1:
                    code = ord(literal_char[0])
                else:
                    code = int(hexcp, 16)
                mapping[name] = code
                mapping[klass] = code
            except Exception:
                continue

    return mapping


def write_glyphmap(path: Path, mapping: Dict[str, int]) -> None:
    # Write as a flat dict of name -> hex codepoint string
    data = {name: f"{code:04x}" for name, code in sorted(mapping.items())}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
