from dataclasses import dataclass

from ttkbootstrap_icons.providers import BaseFontProvider


@dataclass
class WeatherFontProvider(BaseFontProvider):
    name: str = "weather"
    package: str = "ttkbootstrap_icons_weather"
    font_filename: str = ""
    glyphmap_filename: str = "glyphmap.json"

    def display_name(self) -> str:  # pragma: no cover
        return "Weather Icons"
