from ttkbootstrap_icons.providers import BaseFontProvider


class EvaProvider(BaseFontProvider):
    """Initialize the provider with style configuration.

    Uses a single font file (`eva-icons.ttf`) for all styles. Style selection
    is performed by predicates that test for the suffix.
    """

    def __init__(self):
        super().__init__(
            name="eva",
            display_name="Eva Icons",
            package="ttkbootstrap_icons_eva",
            default_style="fill",
            styles={
                "outline": {"filename": "fonts/eva-icons.ttf", "predicate": EvaProvider._is_outline_style},
                "fill": {"filename": "fonts/eva-icons.ttf", "predicate": EvaProvider._is_fill_style}
            }
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
