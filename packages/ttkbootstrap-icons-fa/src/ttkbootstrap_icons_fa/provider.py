from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class FontAwesomeFontProvider(BaseFontProvider):
    name: str = "fa"
    package: str = "ttkbootstrap_icons_fa"
    # Leave empty to auto-detect a .ttf in packaged fonts/
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"
