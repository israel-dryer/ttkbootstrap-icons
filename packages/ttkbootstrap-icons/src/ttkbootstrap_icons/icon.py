import json
import os
import tempfile
from abc import ABC
from importlib.resources import files
from typing import Any, Optional

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageTk import PhotoImage
from .providers import BaseFontProvider

_transparent_image_cache = {}


def create_transparent_icon(size: int = 16) -> PhotoImage:
    """
    Create a fully transparent PIL image of the given size.

    Args:
        size: Tuple specifying (width, height) of the transparent image.

    Returns:
        A PIL.Image object with RGBA mode and full transparency.
    """
    if size in _transparent_image_cache:
        return _transparent_image_cache.get(size)
    else:
        img = Image.new("RGBA", (size, size), (255, 0, 0, 0))
        pm = PhotoImage(image=img)
        _transparent_image_cache[size] = pm
        return pm


class Icon(ABC):
    _icon_map: dict[str, str] = {}
    _font_path: Optional[str] = None
    _cache: dict[tuple[str, int, str, str], PhotoImage] = {}
    _initialized: bool = False
    _icon_set: str = ""

    def __init__(self, name: str, size: int = 24, color: str = "black"):
        """
        Initialize a new  icon instance.

        Args:
            name: The name of the icon to render (must exist in the icon map).
            size: The desired size of the icon in pixels.
            color: The fill color to use when rendering the icon.
        """
        if not self._initialized:
            raise RuntimeError("Icon.initialize() must be called before creating icons.")

        self.name = name
        self.size = size
        self.color = color
        self._img: Optional[PhotoImage] = self._render()

    @property
    def image(self):
        return self._img

    @classmethod
    def _configure(cls, font_path: str, icon_map: dict[str, Any] | list[dict[str, Any]]):
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font not found: {font_path}")

        cls._icon_map = {}

        if isinstance(icon_map, list):
            # Lucide-style (list of dicts)
            items = icon_map
        elif isinstance(icon_map, dict):
            # Determine Lucide-style dict vs Bootstrap
            sample_val = next(iter(icon_map.values()))
            if isinstance(sample_val, dict):
                # Lucide-style dict of dicts
                items = [{"name": k, **v} for k, v in icon_map.items()]
            else:
                # Bootstrap flat dict
                for name, code in icon_map.items():
                    try:
                        codepoint = int(code, 16) if isinstance(code, str) else int(code)
                        cls._icon_map[name] = chr(codepoint)
                    except Exception as e:
                        print(f"Skipped icon '{name}': {e}")
                cls._font_path = font_path
                cls._initialized = True
                return
        else:
            raise TypeError("icon_map must be a list or dict")

        # Process Lucide-style items
        for icon in items:
            name = icon.get("name")
            code_str = icon.get("encodedCode") or icon.get("unicode")
            if not name or not code_str:
                continue
            try:
                if isinstance(code_str, str):
                    code_str = code_str.lstrip("\\").lstrip("0x")
                    codepoint = int(code_str, 16)
                else:
                    codepoint = int(code_str)
                cls._icon_map[name] = chr(codepoint)
            except Exception as e:
                print(f"Skipped icon '{name}': {e}")

        cls._font_path = font_path
        cls._initialized = True

    def _render(self) -> PhotoImage:
        """
        Render the icon as a `PhotoImage`, using PIL and caching the result.

        Returns:
            A `PhotoImage` object.

        Raises:
            ValueError: If the icon name does not exist in the icon map.
        """
        key = (self.name, self.size, self.color, self._icon_set)
        if key in Icon._cache:
            return Icon._cache[key]

        if self.name == "none":
            return create_transparent_icon(self.size)

        glyph = self._icon_map.get(self.name)
        if not glyph:
            raise ValueError(f"Icon '{self.name}' not found in icon map.")

        font = ImageFont.truetype(self._font_path, self.size)

        bbox = font.getbbox(glyph)
        glyph_w, glyph_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        ascent, descent = font.getmetrics()
        full_height = ascent + descent

        canvas_size = self.size
        img = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        dx = (canvas_size - glyph_w) // 2 - bbox[0]
        dy = (canvas_size - full_height) // 2 + (ascent - bbox[3])

        draw.text((dx, dy), glyph, font=font, fill=self.color)

        tk_img = PhotoImage(image=img)
        Icon._cache[key] = tk_img
        return tk_img

    @classmethod
    def initialize(cls, icon_set: str):
        """
        Initialize the Lucide icon system by loading font and icon map from package assets.
        """
        cls._icon_set = icon_set
        assets = files("ttkbootstrap_icons.assets")
        font_data = assets.joinpath(f"{icon_set}.ttf").read_bytes()
        json_text = assets.joinpath(f"{icon_set}.json").read_text(encoding="utf-8")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ttf") as tmp_font:
            tmp_font.write(font_data)
            font_path = tmp_font.name

        icon_map = json.loads(json_text)
        cls._configure(font_path=font_path, icon_map=icon_map)

    @classmethod
    def initialize_with_provider(cls, provider: BaseFontProvider):
        """Initialize icon rendering using an external provider.

        The provider supplies font bytes and a glyph map JSON. We write the
        font to a temporary file and configure the renderer.
        """
        # Avoid re-loading if already initialized for this provider
        if cls._initialized and cls._icon_set == provider.name:
            return
        cls._icon_set = provider.name
        font_data, json_text = provider.load_assets()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ttf") as tmp_font:
            tmp_font.write(font_data)
            font_path = tmp_font.name
        icon_map = json.loads(json_text)
        cls._configure(font_path=font_path, icon_map=icon_map)

    @classmethod
    def cleanup(cls):
        """Remove the temporary font file and reset all internal icon state"""
        if cls._font_path and os.path.exists(cls._font_path):
            try:
                os.remove(cls._font_path)
            except Exception as e:
                raise Exception(f"Error cleaning up icon: {e}")
        cls._initialized = False
        cls._icon_map.clear()
        cls._cache.clear()
        cls._font_path = None

    def __str__(self):
        return str(self._img)
