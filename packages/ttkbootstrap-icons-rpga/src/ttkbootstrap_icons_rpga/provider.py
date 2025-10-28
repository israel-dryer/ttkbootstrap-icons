from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class RPGAFontProvider(BaseFontProvider):
    name: str = "rpga"
    package: str = "ttkbootstrap_icons_rpga"
    font_filename: str = "fonts/rpgawesome-webfont.ttf"
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "RPG Awesome"

