from tkinter_icons.providers import BaseFontProvider


class MeteoconsFontProvider(BaseFontProvider):
    """Provider for Meteocons, a compact weather set by Alessio Atzeni.

    The metadata here pointed at basmilius/weather-icons until 1.1.0, which is a
    different project entirely - an SVG set, not this 47-glyph font. The font's
    own embedded name records identify the author, and they are what these
    values now follow. There is no license *file* upstream: the terms live on
    the author's page and inside the font, so `license_url` is that page.
    """

    def __init__(self):
        super().__init__(
            name="meteocons",
            display_name="Meteocons",
            package="tkinter_icons_meteocons",
            filename="fonts/meteocons.ttf",
            homepage="https://www.alessioatzeni.com/meteocons/",
            license_url="https://www.alessioatzeni.com/meteocons/",
            icon_version="1.0",
            scale_to_fit=True,
        )
