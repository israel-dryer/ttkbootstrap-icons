from ttkbootstrap_icons.providers import BaseFontProvider


class FluentProvider(BaseFontProvider):
    """Initialize the provider with style configuration"""

    def __init__(self):
        super().__init__(
            name="fluent",
            display_name="Fluent Icons Icons",
            package="ttkbootstrap_icons_fluent",
            default_style="regular",
            styles={
                "regular": {"filename": "fonts/FluentSystemIcons-Regular.ttf"},
                "filled": {"filename": "fonts/FluentSystemIcons-Filled.ttf"},
                "light": {"filename": "fonts/FluentSystemIcons-Light.ttf"},
            }
        )

    @staticmethod
    def format_glyph_name(glyph_name: str) -> str:
        """Display friendly name for font name"""
        return str(glyph_name).lower().replace(
            '-regular', '').replace(
            "-filled", "").replace(
            "-light", "").replace(
            "ic-fluent-", ""
        )
