from __future__ import annotations

import json
import os
import tempfile
from abc import ABC
from tkinter import PhotoImage as TkPhotoImage
from typing import Any, ClassVar, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageTk import PhotoImage

from .providers import BaseFontProvider
from .stateful_icon_mixin import StatefulIconMixin


def create_transparent_icon(size: int = 16) -> TkPhotoImage:
    """Return or create a transparent placeholder image of given size."""
    return Icon._get_transparent(size)


class Icon(StatefulIconMixin, ABC):
    """Base class for rendered TTF-based icons (PIL -> PhotoImage).

    Performance features:
      - Class-level caches for rendered images and PIL fonts.
      - Class-level cache for transparent placeholders.
      - Reuses a temporary font file per (provider, style).
      - __slots__ to reduce per-instance overhead.
    """
    __slots__ = ("name", "size", "color", "_img", "_font_path", "_icon_set_id")

    _icon_map: ClassVar[dict[str, Any]] = {}
    _current_font_path: ClassVar[Optional[str]] = None
    _initialized: ClassVar[bool] = False
    _icon_set: ClassVar[str] = ""

    _cache: ClassVar[dict[Tuple[str, int, str, str], PhotoImage]] = {}
    _font_cache: ClassVar[dict[Tuple[str, int], ImageFont.FreeTypeFont]] = {}
    _transparent_cache: ClassVar[dict[int, PhotoImage]] = {}
    _fontfile_cache: ClassVar[dict[str, str]] = {}
    _icon_map_cache: ClassVar[dict[str, dict[str, Any]]] = {}
    _render_params_cache: ClassVar[dict[str, dict[str, Any]]] = {}

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
        self._font_path = Icon._current_font_path
        self._icon_set_id = Icon._icon_set
        self._img: Optional[TkPhotoImage] = self._render()
        super().__init__()
        self._ensure_original_image()

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
        fp = self._font_path
        icon_map = Icon._icon_map_cache.get(self._icon_set_id, Icon._icon_map)

        render_params = Icon._render_params_cache.get(
            self._icon_set_id, {
                "pad_factor": 0.10,
                "y_bias": 0.0,
                "scale_to_fit": True,
            })
        pad_factor = render_params["pad_factor"]
        y_bias = render_params["y_bias"]
        scale_to_fit = render_params["scale_to_fit"]

        key = (self.name, self.size, self.color, fp or "")
        cached = Icon._cache.get(key)
        if cached is not None:
            return cached

        glyph_val = icon_map.get(self.name)
        if glyph_val is None:
            return Icon._get_transparent(self.size)
        glyph = chr(glyph_val) if isinstance(glyph_val, int) else str(glyph_val)

        if not fp:
            return Icon._get_transparent(self.size)

        canvas_size = self.size
        pad = int(self.size * pad_factor)
        inner_w = canvas_size - 2 * pad
        inner_h = canvas_size - 2 * pad

        eff_size = max(1, int(self.size))
        fkey = (fp, eff_size)
        font = Icon._font_cache.get(fkey)
        if font is None:
            font = ImageFont.truetype(fp, eff_size)
            Icon._font_cache[fkey] = font

        ascent, descent = font.getmetrics()
        bbox = font.getbbox(glyph)
        glyph_w = bbox[2] - bbox[0]
        glyph_h = bbox[3] - bbox[1]

        if scale_to_fit and (glyph_w > inner_w or glyph_h > inner_h):
            scale = min(inner_w / max(glyph_w, 1), inner_h / max(glyph_h, 1)) * 0.95
            scaled_size = max(1, int(eff_size * scale))
            fkey_scaled = (fp, scaled_size)
            font = Icon._font_cache.get(fkey_scaled)
            if font is None:
                font = ImageFont.truetype(fp, scaled_size)
                Icon._font_cache[fkey_scaled] = font
            ascent, descent = font.getmetrics()
            bbox = font.getbbox(glyph)
            glyph_w = bbox[2] - bbox[0]
            glyph_h = bbox[3] - bbox[1]

        full_height = ascent + descent

        img = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        dx = pad + (inner_w - glyph_w) // 2 - bbox[0]
        dy = pad + (inner_h - full_height) // 2 + (ascent - bbox[3])
        if y_bias:
            dy += int(self.size * y_bias)

        draw.text((dx, dy), glyph, font=font, fill=self.color)

        pm = PhotoImage(image=img)
        Icon._cache[key] = pm
        return pm

    @classmethod
    def initialize_with_provider(cls, provider: BaseFontProvider, style: str | None = None):
        """Initialize icon rendering using an external provider."""
        icon_set_id = f"{provider.name}:{style or 'default'}"
        if Icon._initialized and Icon._icon_set == icon_set_id:
            return
        Icon._icon_set = icon_set_id

        Icon._render_params_cache[icon_set_id] = {
            "pad_factor": provider.pad_factor,
            "y_bias": provider.y_bias,
            "scale_to_fit": provider.scale_to_fit,
        }

        font_path = Icon._fontfile_cache.get(icon_set_id)
        if not font_path or not os.path.exists(font_path):
            font_bytes, json_text = provider.load_assets(style=style)
            suffix = ".otf" if len(font_bytes) > 4 and font_bytes[:4] == b'OTTO' else ".ttf"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_font:
                tmp_font.write(font_bytes)
                font_path = tmp_font.name
            Icon._fontfile_cache[icon_set_id] = font_path
        else:
            _, json_text = provider.load_assets(style=style)

        icon_map_data = json.loads(json_text)
        cls._configure(font_path=font_path, icon_map=icon_map_data)
        Icon._icon_map_cache[icon_set_id] = Icon._icon_map.copy()

    @classmethod
    def cleanup(cls):
        """Remove all temporary font files and reset internal icon state."""
        for font_path in Icon._fontfile_cache.values():
            if font_path and os.path.exists(font_path):
                try:
                    os.remove(font_path)
                except Exception:
                    pass

        Icon._initialized = False
        Icon._icon_map.clear()
        Icon._icon_map_cache.clear()
        Icon._cache.clear()
        Icon._font_cache.clear()
        Icon._fontfile_cache.clear()
        Icon._current_font_path = None

    def __str__(self):
        return str(self._img)
