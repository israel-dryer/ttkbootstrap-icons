from __future__ import annotations

from tkinter_icons.providers import BaseFontProvider


class BootstrapFontProvider(BaseFontProvider):
    """Provider for the Bootstrap Icons dataset.

    Bootstrap ships two styles - "outline" and "fill" - encoded by the presence of a
    "-fill" suffix in the raw glyph name. Both styles share the same font file and
    are separated via a predicate per style.

    Attributes:
        name: Provider identifier ("bootstrap").
        display_name: Human-friendly name ("Bootstrap").
        default_style: Default style ("outline").
        styles: Map of style -> {filename, predicate}.
    """

    def __init__(self):
        """Initialize the provider with style configuration.

        Uses a single font file (`bootstrap.ttf`) for both styles. Style selection
        is performed by predicates that test for the ``-fill`` suffix.

        Note:
            The provider expects glyphmaps named `glyphmap.json` (single-file) or
            `glyphmap-<style>.json` when styles require separate maps.
        """
        super().__init__(
            name="bootstrap",
            display_name="Bootstrap Icons",
            package="tkinter_icons_bs.assets",
            homepage="https://icons.getbootstrap.com/",
            license_url="https://github.com/twbs/icons/blob/main/LICENSE",
            icon_version="1.13.1",
            default_style="outline",
            # No y_bias: the small downward nudge this used to carry was
            # compensating for getbbox under-reporting glyph ink. Centering now
            # works from the measured ink in metrics.json, which lands the glyph
            # dead center on its own — the old bias visibly pushes it low.
            styles={
                "fill": {"filename": "bootstrap.ttf", "predicate": BootstrapFontProvider._is_fill_style},
                "outline": {"filename": "bootstrap.ttf", "predicate": BootstrapFontProvider._is_outline_style},
            }
        )

    @staticmethod
    def _is_outline_style(name: str) -> bool:
        return '-fill' not in name

    @staticmethod
    def _is_fill_style(name: str) -> bool:
        return '-fill' in name