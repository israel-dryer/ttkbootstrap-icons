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

    def display_name(self) -> str:  # pragma: no cover
        return "Font Awesome"

    def style_display_name(self, style: str) -> str:  # pragma: no cover
        mapping = {"solid": "Solid", "regular": "Regular", "brands": "Brands"}
        return mapping.get(style, super().style_display_name(style))
