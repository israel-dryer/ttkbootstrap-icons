from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class MaterialFontProvider(BaseFontProvider):
    name: str = "mat"
    package: str = "ttkbootstrap_icons_mat"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Material Design Icons"
