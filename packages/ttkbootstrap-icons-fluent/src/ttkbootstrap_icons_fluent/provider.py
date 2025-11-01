from ttkbootstrap_icons.providers import BaseFontProvider


class FluentSystemFontProvider(BaseFontProvider):
    """Initialize the provider with style configuration"""

    def __init__(self):
        super().__init__(
            name="fluent",
            display_name="Fluent System Icons",
            package="ttkbootstrap_icons_fluent",
            homepage="https://github.com/microsoft/fluentui-system-icons",
            license_url="https://github.com/microsoft/fluentui-system-icons/blob/main/LICENSE",
            icon_version="1.1.261",
            default_style="regular",
            styles={
                "regular": {"filename": "fonts/FluentSystemIcons-Regular.ttf"},
                "filled": {"filename": "fonts/FluentSystemIcons-Filled.ttf"},
                "light": {"filename": "fonts/FluentSystemIcons-Light.ttf"},
            },
            scale_to_fit=True,
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
