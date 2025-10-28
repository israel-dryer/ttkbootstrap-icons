import os
import json
import tempfile
from typing import Literal

from ttkbootstrap_icons.icon import Icon
from .provider import EvaFontProvider


EvaStyle = Literal["outline", "fill"]


def _resolve_name_with_map(name: str, style: EvaStyle) -> str:
    # Normalize and short-circuit the transparent placeholder
    low = (name or "").lower()
    if low == "none":
        return "none"

    # Access the loaded icon map (populated after initialize_with_provider)
    mp = Icon._icon_map

    # If an explicit suffix is provided in the name, honor it with Eva-specific rules:
    # - "-outline" entries exist as-is in the glyph map
    # - Eva does not encode "-fill" in glyph names; treat "*-fill" as the base name when possible
    if low.endswith("-outline"):
        return low
    if low.endswith("-fill"):
        base = low[:-5]
        if base in mp:
            return base
        # If a provider ever includes explicit -fill keys, allow them; otherwise fall back to base
        return low if low in mp else base

    # No explicit suffix in the name; resolve by requested style
    if style == "outline":
        cand = f"{low}-outline"
        print("cand: ", cand, "icon map", mp)
        if cand in mp:
            return cand
        # Fallback to base if outline variant missing
        return low
    else:  # fill
        # Prefer the base name for fill since Eva encodes fills without a suffix
        if low in mp:
            return low
        # As a safety net, accept a "-fill" entry if present
        cand = f"{low}-fill"
        return cand if cand in mp else low


class EvaIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black", style: EvaStyle = "fill"):
        EvaIcon.initialize_with_provider(EvaFontProvider())
        # Fallback: If the icon map is unexpectedly empty (dev envs, reloads),
        # load assets directly and reconfigure so resolution works reliably.
        if not Icon._icon_map:
            try:
                prov = EvaFontProvider()
                font_bytes, gm_text = prov.load_assets()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".ttf") as tmp_font:
                    tmp_font.write(font_bytes)
                    font_path = tmp_font.name
                Icon._configure(font_path=font_path, icon_map=json.loads(gm_text))
            except Exception:
                pass
        resolved = _resolve_name_with_map(name, style)
        print("resolved: ", resolved, "name: ", name, "style: ", style)
        if os.environ.get("TTKICONS_DEBUG"):
            try:
                print(f"[ttkicons DEBUG] provider=eva style={style} name={name} -> resolved={resolved}")
            except Exception:
                pass
        super().__init__(resolved, size, color)
