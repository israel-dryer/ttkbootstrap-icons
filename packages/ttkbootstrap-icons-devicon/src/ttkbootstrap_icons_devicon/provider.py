import re

from ttkbootstrap_icons.providers import BaseFontProvider


class DeviconProvider(BaseFontProvider):
    def __init__(self):
        """Initialize the provider with style configuration.

        Uses a single font file (`devicon.ttf`) for all styles. Style selection
        is performed by predicates that test for the suffix.

        Note:
            The provider expects glyphmaps named `glyphmap.json` (single-file) or
            `glyphmap-<style>.json` when styles require separate maps.
        """
        super().__init__(
            name="devicon",
            package="ttkbootstrap_icons_devicon",
            default_style="plain",
            styles={
                "plain": {"filename": "fonts/devicon.ttf"},
                "plain-wordmark": {"filename": "fonts/devicon.ttf"},
                "original": {"filename": "fonts/devicon.ttf"},
                "original-wordmark": {"filename": "fonts/devicon.ttf"}
            }
        )

    @staticmethod
    def _is_plain_style(name: str) -> bool:
        return '-plain' in name

    @staticmethod
    def _is_plain_wordmark_style(name: str) -> bool:
        return '-plain-wordmark' in name

    @staticmethod
    def _is_original_style(name: str) -> bool:
        return '-original' in name

    @staticmethod
    def _is_original_wordmark_style(name: str) -> bool:
        return '-original-wordmark' in name

    @staticmethod
    def format_glyph_name(glyph_name: str) -> str:
        """Display friendly name for font name"""
        suffix_anywhere = re.compile(r'-(?:plain|original)(?:-wordmark)?', re.IGNORECASE)
        return suffix_anywhere.sub("", str(glyph_name).lower())
