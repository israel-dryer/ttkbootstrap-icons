from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class RemixFontProvider(BaseFontProvider):
    name: str = "remix"
    package: str = "ttkbootstrap_icons_remix"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"

