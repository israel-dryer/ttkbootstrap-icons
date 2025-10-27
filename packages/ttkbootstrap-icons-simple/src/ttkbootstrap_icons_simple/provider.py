from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class SimpleFontProvider(BaseFontProvider):
    name: str = "simple"
    package: str = "ttkbootstrap_icons_simple"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Simple Icons"
