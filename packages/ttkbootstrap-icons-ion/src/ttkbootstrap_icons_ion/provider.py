from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class IonFontProvider(BaseFontProvider):
    name: str = "ion"
    package: str = "ttkbootstrap_icons_ion"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Ionicons"
