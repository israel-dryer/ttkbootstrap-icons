from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Tuple


@dataclass
class BaseFontProvider(ABC):
    """Base provider for font-based icon sets.

    Subclasses should set:
    - name: short identifier (e.g., "bootstrap", "lucide", "fa")
    - package: the package where assets live
    - font_filename: path (relative to package) to a .ttf font
    - glyphmap_filename: path (relative to package) to the icon JSON map
    """

    name: str
    package: str
    font_filename: str
    glyphmap_filename: str

    def load_assets(self) -> Tuple[bytes, str]:
        """Return (font_bytes, glyphmap_json_text)."""
        pkg = files(self.package)

        # Resolve font file: explicit filename or first .ttf in fonts/
        if self.font_filename:
            font_path = pkg.joinpath(self.font_filename)
        else:
            # Fallback: pick first .ttf under a fonts/ directory
            candidates = list(pkg.rglob("*.ttf"))
            if not candidates:
                raise FileNotFoundError(
                    f"No font found for provider '{self.name}' in package '{self.package}'."
                )
            font_path = candidates[0]

        if not str(font_path).endswith(".ttf"):
            raise FileNotFoundError(f"Invalid font path for provider '{self.name}': {font_path}")

        glyphmap_path = pkg.joinpath(self.glyphmap_filename)

        font_bytes = font_path.read_bytes()
        glyphmap_json = glyphmap_path.read_text(encoding="utf-8")
        return font_bytes, glyphmap_json


class BuiltinBootstrapProvider(BaseFontProvider):
    def __init__(self) -> None:
        super().__init__(
            name="bootstrap",
            package="ttkbootstrap_icons.assets",
            font_filename="bootstrap.ttf",
            glyphmap_filename="bootstrap.json",
        )


class BuiltinLucideProvider(BaseFontProvider):
    def __init__(self) -> None:
        super().__init__(
            name="lucide",
            package="ttkbootstrap_icons.assets",
            font_filename="lucide.ttf",
            glyphmap_filename="lucide.json",
        )

