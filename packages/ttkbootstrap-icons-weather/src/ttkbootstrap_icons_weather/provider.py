from ttkbootstrap_icons.providers import BaseFontProvider


class WeatherProvider(BaseFontProvider):
    """Initialize the provider"""

    def __init__(self):
        super().__init__(
            name="weather",
            display_name="Weather Icons",
            package="ttkbootstrap_icons_weather",
            filename="fonts/weathericons-regular-webfont.ttf",
            scale_to_fit=True,
        )
