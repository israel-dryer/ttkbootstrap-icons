from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class EvaFontProvider(BaseFontProvider):
    name: str = "eva"
    package: str = "ttkbootstrap_icons_eva"
    font_filename: str = "fonts/eva-icons.ttf"
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Eva Icons"

    def list_styles(self) -> list[str]:  # outline/fill variants encoded in names
        return ["outline", "fill"]

    def get_default_style(self) -> str | None:  # pragma: no cover
        return "fill"
