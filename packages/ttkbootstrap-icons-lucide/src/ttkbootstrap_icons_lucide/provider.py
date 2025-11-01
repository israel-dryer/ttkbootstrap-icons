from ttkbootstrap_icons.providers import BaseFontProvider


class LucideFontProvider(BaseFontProvider):
    """Initialize the provider with style configuration.

    Uses a single font file (`lucide.ttf`) for all styles. Style selection
    is performed by predicates that test for the suffix.
    """

    def __init__(self):
        super().__init__(
            name="lucide",
            display_name="Lucide Icons",
            package="ttkbootstrap_icons_lucide",
            homepage="http://lucide.dev/icons/",
            license_url="https://lucide.dev/license",
            icon_version="0.511.0",
            filename="fonts/lucide.ttf",
            scale_to_fit=True,
        )

    @staticmethod
    def format_glyph_name(glyph_name: str) -> str:
        """Display friendly name for font name"""
        return str(glyph_name).lower().replace("icon-", "")
