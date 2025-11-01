import re

from ttkbootstrap_icons.providers import BaseFontProvider


class DeviconFontProvider(BaseFontProvider):
    def __init__(self):
        """Initialize the provider with style configuration.

        Uses a single font file (`devicon.ttf`) for all styles. Style selection
        is performed by predicates that test for the suffix.
        """
        super().__init__(
            name="devicon",
            display_name="Devicon",
            package="ttkbootstrap_icons_devicon",
            homepage="https://devicon.dev/",
            license_url="https://github.com/devicons/devicon/blob/master/LICENSE",
            icon_version="2.17.0",
            default_style="plain",
            styles={
                "plain": {"filename": "fonts/devicon.ttf", "predicate": DeviconFontProvider._is_plain_style},
                "plain-wordmark": {"filename": "fonts/devicon.ttf",
                                   "predicate": DeviconFontProvider._is_plain_wordmark_style},
                "original": {"filename": "fonts/devicon.ttf", "predicate": DeviconFontProvider._is_original_style},
                "original-wordmark": {"filename": "fonts/devicon.ttf",
                                      "predicate": DeviconFontProvider._is_original_wordmark_style}
            },
            pad_factor=0.15,
            scale_to_fit=True,
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
