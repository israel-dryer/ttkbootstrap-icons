from ttkbootstrap_icons.providers import BaseFontProvider


class MeteoconsProvider(BaseFontProvider):
    """Initialize the provider"""

    def __init__(self):
        super().__init__(
            name="meteocons",
            display_name="Meteocons",
            package="ttkbootstrap_icons_meteocons",
            filename="fonts/meteocons.ttf",
            homepage="https://bas.dev/work/meteocons",
            license_url="https://github.com/basmilius/weather-icons/blob/dev/LICENSE",
            icon_version="2.0.0",
            scale_to_fit=True,
        )
