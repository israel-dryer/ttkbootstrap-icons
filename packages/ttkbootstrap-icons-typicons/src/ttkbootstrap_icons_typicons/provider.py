from ttkbootstrap_icons.providers import BaseFontProvider


class TypiconsProvider(BaseFontProvider):
    """Provider for the Typicons font.

    Uses a single font file (`typicons.ttf`) for all styles. Style selection
    is performed by predicates that test for the suffix.
    """

    def __init__(self):
        super().__init__(
            name="typicons",
            display_name="Typicons",
            package="ttkbootstrap_icons_typicons",
            homepage="https://www.s-ings.com/typicons/",
            license_url="https://github.com/stephenhutchings/typicons.font/blob/master/LICENCE.md",
            icon_version="2.1.2",
            default_style="fill",
            styles={
                "outline": {"filename": "fonts/typicons.ttf", "predicate": TypiconsProvider._is_outline_style},
                "fill": {"filename": "fonts/typicons.ttf", "predicate": TypiconsProvider._is_fill_style}
            },
            scale_to_fit=True,
        )

    @staticmethod
    def _is_fill_style(name: str) -> bool:
        return not name.endswith("-outline")

    @staticmethod
    def _is_outline_style(name: str) -> bool:
        return name.endswith("-outline")

    @staticmethod
    def format_glyph_name(glyph_name: str) -> str:
        """Display friendly name for font name"""
        return str(glyph_name).lower().replace('-outline', '')
