from tkinter_icons.providers import BaseFontProvider


class WeatherFontProvider(BaseFontProvider):
    """Initialize the provider"""

    def __init__(self):
        super().__init__(
            name="weather",
            display_name="Weather Icons",
            package="tkinter_icons_weather",
            filename="fonts/weathericons-regular-webfont.ttf",
            homepage="https://erikflowers.github.io/weather-icons/",
            # Weather Icons has no LICENSE file; upstream states its terms in the
            # README, which is why this points at a heading anchor rather than a
            # file. It pointed at the Typicons licence until 5.0.0 - a copy-paste
            # that the browser turned into a "License" link opening the wrong
            # project's terms.
            license_url="https://github.com/erikflowers/weather-icons#licensing",
            icon_version="2.0.10",
            scale_to_fit=True,
        )
