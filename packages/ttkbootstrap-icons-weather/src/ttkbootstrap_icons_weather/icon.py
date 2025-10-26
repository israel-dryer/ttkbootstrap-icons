from ttkbootstrap_icons.icon import Icon
from .provider import WeatherFontProvider


class WeatherIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black"):
        WeatherIcon.initialize_with_provider(WeatherFontProvider())
        super().__init__(name, size, color)

