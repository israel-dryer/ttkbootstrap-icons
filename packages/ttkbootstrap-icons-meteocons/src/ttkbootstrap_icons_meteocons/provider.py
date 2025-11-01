from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class MeteoconsFontProvider(BaseFontProvider):
    name: str = "meteocons"
    package: str = "ttkbootstrap_icons_meteocons"
    # Leave blank to auto-detect first .ttf/.otf under package (fonts/ preferred)
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Meteocons"

