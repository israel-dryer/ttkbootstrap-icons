from ttkbootstrap_icons.providers import BaseFontProvider


class WeatherFontProvider(BaseFontProvider):
    """Initialize the provider"""

    def __init__(self):
        super().__init__(
            name="weather",
            display_name="Weather Icons",
            package="ttkbootstrap_icons_weather",
            filename="fonts/weathericons-regular-webfont.ttf",
            homepage="https://erikflowers.github.io/weather-icons/",
            license_url="https://github.com/stephenhutchings/typicons.font/blob/master/LICENCE.md",
            icon_version="2.0.10",
            scale_to_fit=True,
        )
