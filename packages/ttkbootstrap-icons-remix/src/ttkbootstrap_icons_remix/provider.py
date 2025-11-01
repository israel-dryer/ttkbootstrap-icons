from ttkbootstrap_icons.providers import BaseFontProvider


class RemixFontProvider(BaseFontProvider):
    """Initialize the provider with style configuration.

    Uses a single font file (`remixicon.ttf`) for all styles. Style selection
    is performed by predicates that test for the suffix.
    """

    def __init__(self):
        super().__init__(
            name="remix",
            display_name="Remix Icon",
            package="ttkbootstrap_icons_remix",
            homepage="https://remixicon.com/",
            license_url="https://github.com/Remix-Design/RemixIcon/blob/master/License",
            icon_version="4.7.0",
            default_style="fill",
            styles={
                "line": {"filename": "fonts/remixicon.ttf", "predicate": RemixFontProvider._is_line_style},
                "fill": {"filename": "fonts/remixicon.ttf", "predicate": RemixFontProvider._is_fill_style}
            },
            pad_factor=0.15,
            scale_to_fit=True,
        )

    @staticmethod
    def _is_line_style(name: str) -> bool:
        return name.endswith("-line")

    @staticmethod
    def _is_fill_style(name: str) -> bool:
        return name.endswith("-fill")

    @staticmethod
    def format_glyph_name(glyph_name: str) -> str:
        """Display friendly name for font name"""
        return str(glyph_name).lower().replace('-outline', '').replace('-fill', '')
