from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class SimpleFontProvider(BaseFontProvider):
    name: str = "simple"
    package: str = "ttkbootstrap_icons_simple"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"

