from typing import Literal

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_gmi.provider import GoogleMaterialIconFontProvider

GMatStyles = Literal['baseline', 'outlined', 'round', 'sharp']


class GMatIcon(Icon):
    """Convenience icon for the GMI Icon glyph set.

    Resolves the provided name (optionally with a style) using `GMIProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name. May be a friendly name (e.g. "home") or a raw glyph
            (e.g. "home-outlined"). If you pass a conflicting style (e.g. name ends
            with "-outlined" but you set `style="round"`), a `ValueError` is raised.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").
        style: Optional style override: "baseline", "outlined", "round", "sharp". If omitted, the provider's default style is used.

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", style: GMatStyles | None = None):
        prov = GoogleMaterialIconFontProvider()
        # Resolve the style from the name if not explicitly provided
        resolved_style = prov.resolve_icon_style(name, style)
        GMatIcon.initialize_with_provider(prov, resolved_style)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)
