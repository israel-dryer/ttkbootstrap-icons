from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from importlib.resources import files
import os
from pathlib import Path
from typing import Optional, Tuple


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

    def display_name(self) -> str:
        return getattr(self, "display", self.name)

    def style_display_name(self, style: str) -> str:
        return style.title()
    def list_styles(self) -> list[str]:
        """Return available style identifiers for this provider (if any)."""
        return []

    def get_default_style(self) -> str | None:
        """Return the default style identifier, if any."""
        return None

    def load_assets(self, style: Optional[str] = None) -> Tuple[bytes, str]:
        """Return (font_bytes, glyphmap_json_text)."""
        pkg = files(self.package)

        # Resolve font file: explicit filename or first .ttf/.otf in fonts/
        if self.font_filename:
            font_path = pkg.joinpath(self.font_filename)
        else:
            # Fallback: pick first .ttf or .otf under package
            candidates = list(pkg.rglob("*.ttf")) + list(pkg.rglob("*.otf"))
            if not candidates:
                raise FileNotFoundError(
                    f"No font found for provider '{self.name}' in package '{self.package}'."
                )
            font_path = candidates[0]

        # Ensure the file exists
        try:
            _ = font_path.read_bytes()
        except Exception as e:
            raise FileNotFoundError(f"Font not accessible for provider '{self.name}': {font_path}") from e

        glyphmap_path = pkg.joinpath(self.glyphmap_filename)

        # Debug output for troubleshooting which font is being loaded
        if os.environ.get("TTKICONS_DEBUG"):
            try:
                print(f"[ttkicons DEBUG] provider={self.name} style={style or ''} font={font_path}")
            except Exception:
                pass

        font_bytes = font_path.read_bytes()
        glyphmap_json = glyphmap_path.read_text(encoding="utf-8")
        return font_bytes, glyphmap_json


@dataclass
class MultiStyleFontProvider(BaseFontProvider):
    """Provider that supports multiple styles.

    Set `styles` to a mapping of style -> relative TTF path (under the package).
    If `style` is None, uses a `default_style`.
    """

    styles: dict
    default_style: str = "regular"

    def load_assets(self, style: Optional[str] = None) -> Tuple[bytes, str]:
        chosen = (style or self.default_style).lower()
        if chosen not in self.styles:
            raise FileNotFoundError(f"Style '{chosen}' not found for provider '{self.name}'.")
        self.font_filename = self.styles[chosen]
        return super().load_assets(style=style)

    def list_styles(self) -> list[str]:
        return sorted(self.styles.keys())

    def get_default_style(self) -> str | None:
        return self.default_style


class BuiltinBootstrapProvider(BaseFontProvider):
    def __init__(self) -> None:
        super().__init__(
            name="bootstrap",
            package="ttkbootstrap_icons.assets",
            font_filename="bootstrap.ttf",
            glyphmap_filename="bootstrap.json",
        )

    def display_name(self) -> str:  # pragma: no cover
        return "Bootstrap Icons"


class BuiltinLucideProvider(BaseFontProvider):
    def __init__(self) -> None:
        super().__init__(
            name="lucide",
            package="ttkbootstrap_icons.assets",
            font_filename="lucide.ttf",
            glyphmap_filename="lucide.json",
        )

    def display_name(self) -> str:  # pragma: no cover
        return "Lucide Icons"
