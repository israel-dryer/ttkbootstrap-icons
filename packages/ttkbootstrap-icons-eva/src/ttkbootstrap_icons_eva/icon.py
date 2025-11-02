from typing import Literal

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_eva.provider import EvaFontProvider

EvaStyles = Literal['fill', 'outline']


class EvaIcon(Icon):
    """Convenience icon for the Eva Icons glyph set.

    Resolves the provided name (optionally with a style) using `EvaFontProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name. May be a friendly name (e.g. "award") or a raw glyph
            (e.g. "award-outline"). If you pass a conflicting style (e.g. name ends
            with "-outline" but you set `style="fill"`), a `ValueError` is raised.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").
        style: Optional style override: "fill", "outline". If omitted, the provider's default style is used.
            When `name` already encodes a style suffix (e.g. "-outline"), that suffix takes precedence.

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", style: EvaStyles | None = None):
        prov = EvaFontProvider()
        EvaIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)



