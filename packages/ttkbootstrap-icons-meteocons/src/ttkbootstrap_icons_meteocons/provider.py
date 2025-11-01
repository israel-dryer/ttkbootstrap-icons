from ttkbootstrap_icons.providers import BaseFontProvider


class MeteoconsProvider(BaseFontProvider):
    """Initialize the provider"""

    def __init__(self):
        super().__init__(
            name="meteocons",
            display_name="Meteocons",
            package="ttkbootstrap_icons_meteocons",
            filename="fonts/meteocons.ttf",
            scale_to_fit=True,
        )
