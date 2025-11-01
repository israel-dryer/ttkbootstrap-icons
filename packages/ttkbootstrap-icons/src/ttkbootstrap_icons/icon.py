from __future__ import annotations

import json
import os
import tempfile
from abc import ABC
from typing import Any, Optional, ClassVar, Tuple

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageTk import PhotoImage
from tkinter import PhotoImage as TkPhotoImage

from .providers import BaseFontProvider


def create_transparent_icon(size: int = 16) -> TkPhotoImage:
    """Return or create a transparent placeholder image of given size."""
    return Icon._get_transparent(size)


class Icon(ABC):
    """Base class for rendered TTF-based icons (PIL → PhotoImage).

    Performance features:
      • Class-level caches for rendered images and PIL fonts.
      • Class-level cache for transparent placeholders.
      • Reuses a temporary font file per (provider, style).
      • __slots__ to reduce per-instance overhead.
    """
    __slots__ = ("name", "size", "color", "_img", "_font_path", "_icon_set_id")

    # shared icon-set state
    _icon_map: ClassVar[dict[str, Any]] = {}
    _current_font_path: ClassVar[Optional[str]] = None
    _initialized: ClassVar[bool] = False
    _icon_set: ClassVar[str] = ""
    _pad_factor: ClassVar[float] = 0.10
    _y_bias: ClassVar[float] = 0.0

    # caches
    _cache: ClassVar[dict[Tuple[str, int, str, str], PhotoImage]] = {}  # rendered PhotoImage cache
    _font_cache: ClassVar[dict[Tuple[str, int], ImageFont.FreeTypeFont]] = {}  # PIL font by (path, size)
    _transparent_cache: ClassVar[dict[int, PhotoImage]] = {}  # transparent placeholders
    _fontfile_cache: ClassVar[dict[str, str]] = {}  # icon_set_id -> temp font path
    _icon_map_cache: ClassVar[dict[str, dict[str, Any]]] = {}  # icon_set_id -> icon_map

    def __init__(self, name: str, size: int = 24, color: str = "black"):
        """Create a new icon.

        Args:
            name: Resolved icon key in the icon map.
            size: Pixel size.
            color: Foreground color.
        """
        if not Icon._initialized:
            raise RuntimeError("Icon provider not initialized. Call initialize_with_provider() before creating icons.")

        self.name = name
        self.size = size
        self.color = color
        # Store the current font path and icon_set_id so this instance uses the correct font
        self._font_path = Icon._current_font_path
        self._icon_set_id = Icon._icon_set
        self._img: Optional[TkPhotoImage] = self._render()

    @property
    def image(self) -> TkPhotoImage:
        return self._img

    @classmethod
    def _get_transparent(cls, size: int) -> PhotoImage:
        pm = cls._transparent_cache.get(size)
        if pm is not None:
            return pm
        img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        pm = PhotoImage(image=img)
        cls._transparent_cache[size] = pm
        return pm

    @classmethod
    def _configure(cls, font_path: str, icon_map: dict[str, Any] | list[dict[str, Any]]):
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font not found: {font_path}")

        mapping: dict[str, Any] = {}

        if isinstance(icon_map, list):
            # Lucide-style: list of dicts with fields like {"name": "...", "unicode": "EA01"}
            for entry in icon_map:
                if not isinstance(entry, dict):
                    continue
                name = str(entry.get("name", "")).strip()
                if not name:
                    continue
                uni = entry.get("unicode")
                if uni is None:
                    continue
                try:
                    codepoint = int(uni, 16) if isinstance(uni, str) else int(uni)
                    mapping[name] = chr(codepoint)
                except Exception:
                    # Skip malformed entries
                    continue

        elif isinstance(icon_map, dict):
            # Could be: {'house': 'EA01', ...} (Bootstrap) OR {'house': {'unicode': '...'}, ...} (Lucide dict-of-dicts)
            # Detect dict-of-dicts by sampling the first value
            try:
                sample_val = next(iter(icon_map.values()))
            except StopIteration:
                sample_val = None

            if isinstance(sample_val, dict):
                # Lucide-style dict of dicts
                for name, detail in icon_map.items():
                    if not isinstance(detail, dict):
                        continue
                    uni = detail.get("unicode")
                    if uni is None:
                        continue
                    try:
                        codepoint = int(uni, 16) if isinstance(uni, str) else int(uni)
                        mapping[str(name)] = chr(codepoint)
                    except Exception:
                        continue
            else:
                # Bootstrap flat dict
                for name, code in icon_map.items():
                    try:
                        codepoint = int(code, 16) if isinstance(code, str) else int(code)
                        mapping[str(name)] = chr(codepoint)
                    except Exception:
                        continue
        else:
            raise TypeError("icon_map must be a list[dict] or dict")

        Icon._icon_map = mapping
        Icon._current_font_path = font_path
        Icon._initialized = True

    def _render(self) -> PhotoImage:
        """Render the icon as a `PhotoImage`, using PIL and caching the result."""
        # Use instance font path and look up the icon map for this icon set
        fp = self._font_path
        icon_map = Icon._icon_map_cache.get(self._icon_set_id, Icon._icon_map)

        # Cache key: (name, size, color, font_path)
        key = (self.name, self.size, self.color, fp or "")
        cached = Icon._cache.get(key)
        if cached is not None:
            return cached

        # Glyph lookup
        glyph_val = icon_map.get(self.name)
        if glyph_val is None:
            return Icon._get_transparent(self.size)
        glyph = chr(glyph_val) if isinstance(glyph_val, int) else str(glyph_val)

        # Build or reuse a PIL font for (font_path, size)
        if not fp:
            return Icon._get_transparent(self.size)
        eff_size = max(1, int(self.size))
        fkey = (fp, eff_size)
        font = Icon._font_cache.get(fkey)
        if font is None:
            font = ImageFont.truetype(fp, eff_size)
            Icon._font_cache[fkey] = font

        # Layout
        pad = int(self.size * Icon._pad_factor)
        ascent, descent = font.getmetrics()
        bbox = font.getbbox(glyph)
        glyph_w = bbox[2] - bbox[0]
        full_height = ascent + descent

        canvas_size = self.size
        img = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        inner_w = canvas_size - 2 * pad
        inner_h = canvas_size - 2 * pad
        dx = pad + (inner_w - glyph_w) // 2 - bbox[0]
        dy = pad + (inner_h - full_height) // 2 + (ascent - bbox[3])
        if Icon._y_bias:
            dy += int(self.size * Icon._y_bias)

        draw.text((dx, dy), glyph, font=font, fill=self.color)

        pm = PhotoImage(image=img)
        Icon._cache[key] = pm
        return pm

    @classmethod
    def initialize_with_provider(cls, provider: BaseFontProvider, style: str | None = None):
        """Initialize icon rendering using an external provider.

        Reuses a temp font path per (provider, style) for efficiency.
        """
        icon_set_id = f"{provider.name}:{style or 'default'}"
        if Icon._initialized and Icon._icon_set == icon_set_id:
            return
        Icon._icon_set = icon_set_id

        # Reuse temp font if already created for this icon set
        font_path = Icon._fontfile_cache.get(icon_set_id)
        if not font_path or not os.path.exists(font_path):
            font_bytes, json_text = provider.load_assets(style=style)
            # Use .otf suffix for OpenType fonts, .ttf for TrueType
            # PIL can handle both, but better to be accurate
            suffix = ".otf" if len(font_bytes) > 4 and font_bytes[:4] == b'OTTO' else ".ttf"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_font:
                tmp_font.write(font_bytes)
                font_path = tmp_font.name
            Icon._fontfile_cache[icon_set_id] = font_path
        else:
            # Still need glyphmap JSON for configure
            _, json_text = provider.load_assets(style=style)

        icon_map_data = json.loads(json_text)
        cls._configure(font_path=font_path, icon_map=icon_map_data)
        # Cache the icon map for this icon_set_id
        Icon._icon_map_cache[icon_set_id] = Icon._icon_map.copy()

    @classmethod
    def cleanup(cls):
        """Remove all temporary font files and reset internal icon state."""
        # Clean up all cached font files
        for font_path in Icon._fontfile_cache.values():
            if font_path and os.path.exists(font_path):
                try:
                    os.remove(font_path)
                except Exception:
                    pass  # Ignore cleanup errors

        # Reset all state
        Icon._initialized = False
        Icon._icon_map.clear()
        Icon._icon_map_cache.clear()
        Icon._cache.clear()
        Icon._font_cache.clear()
        Icon._fontfile_cache.clear()
        Icon._current_font_path = None

    def __str__(self):
        return str(self._img)
