from ttkbootstrap_icons.providers import BaseFontProvider


class RemixProvider(BaseFontProvider):
    """Initialize the provider with style configuration.

    Uses a single font file (`remixicon.ttf`) for all styles. Style selection
    is performed by predicates that test for the suffix.
    """

    def __init__(self):
        super().__init__(
            name="eva",
            display_name="Remix Icons",
            package="ttkbootstrap_icons_remix",
            default_style="fill",
            styles={
                "line": {"filename": "fonts/remixicon.ttf", "predicate": RemixProvider._is_line_style},
                "fill": {"filename": "fonts/remixicon.ttf", "predicate": RemixProvider._is_fill_style}
            }
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
