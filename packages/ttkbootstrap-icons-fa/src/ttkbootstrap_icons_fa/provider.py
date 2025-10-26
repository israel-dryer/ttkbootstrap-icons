from dataclasses import dataclass

from ttkbootstrap_icons.providers import MultiStyleFontProvider


@dataclass
class FontAwesomeFontProvider(MultiStyleFontProvider):
    name: str = "fa"
    package: str = "ttkbootstrap_icons_fa"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"
    styles: dict = None  # type: ignore
    default_style: str = "solid"

    def __post_init__(self):
        if self.styles is None:
            self.styles = {
                "solid": "fonts/fa-solid-900.ttf",
                "regular": "fonts/fa-regular-400.ttf",
                "brands": "fonts/fa-brands-400.ttf",
            }
