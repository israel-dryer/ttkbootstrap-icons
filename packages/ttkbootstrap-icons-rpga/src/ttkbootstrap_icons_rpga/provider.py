from ttkbootstrap_icons.providers import BaseFontProvider


class RPGAProvider(BaseFontProvider):
    """Initialize the provider with style configuration.

    Uses a single font file (`rpgawesome-webfont.ttf`) for all styles. Style selection
    is performed by predicates that test for the suffix.
    """

    def __init__(self):
        super().__init__(
            name="rpga",
            display_name="RPG Awesome",
            package="ttkbootstrap_icons_rpga",
            homepage="https://nagoshiashumari.github.io/Rpg-Awesome/",
            license_url="https://github.com/nagoshiashumari/Rpg-Awesome/blob/master/LICENSE.md",
            icon_version="1.0.0",
            filename="fonts/rpgawesome-webfont.ttf",
            pad_factor=0.15,
            scale_to_fit=True,
        )
