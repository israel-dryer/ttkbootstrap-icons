from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class LucideFontProvider(BaseFontProvider):
    name: str = "lucide"
    package: str = "ttkbootstrap_icons_lucide"
    # If local fonts are not shipped yet, you can temporarily fall back by copying
    # assets from the base package into this provider's fonts/ and glyphmap.json.
    font_filename: str = "fonts/lucide.ttf"
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Lucide Icons"

