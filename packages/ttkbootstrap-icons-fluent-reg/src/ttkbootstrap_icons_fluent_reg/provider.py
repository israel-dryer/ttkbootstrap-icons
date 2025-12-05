from ttkbootstrap_icons.providers import BaseFontProvider


class FluentRegularFontProvider(BaseFontProvider):
    """Provider for Fluent System Icons - Regular style only."""

    def __init__(self):
        super().__init__(
            name="fluent-regular",
            display_name="Fluent System Icons (Regular)",
            package="ttkbootstrap_icons_fluent_reg",
            homepage="https://github.com/microsoft/fluentui-system-icons",
            license_url="https://github.com/microsoft/fluentui-system-icons/blob/main/LICENSE",
            icon_version="1.1.261",
            filename="fonts/FluentSystemIcons-Regular.ttf",
            scale_to_fit=True,
        )

    @staticmethod
    def format_glyph_name(glyph_name: str) -> str:
        """Display friendly name for font name"""
        return str(glyph_name).lower().replace(
            '-regular', '').replace(
            "ic-fluent-", ""
        )
