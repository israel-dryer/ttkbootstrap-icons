from typing import Literal

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_fa.provider import FontAwesomeFontProvider

FAStyles = Literal['regular', 'solid', 'brands']


class FAIcon(Icon):
    """Convenience icon for the Font Awesome Icon glyph set.

    Resolves the provided name (optionally with a style) using `FAProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name. May be a friendly name (e.g. "anchor") or a raw glyph
            (e.g. "anchor-solid"). If you pass a conflicting style (e.g. name ends
            with "-outlined" but you set `style="regular"`), a `ValueError` is raised.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").
        style: Optional style override: "regular", "solid", "brands". If omitted, the provider's default style is used.

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", style: FAStyles | None = None):
        prov = FontAwesomeFontProvider()
        # Resolve the style from the name if not explicitly provided
        resolved_style = prov.resolve_icon_style(name, style)
        FAIcon.initialize_with_provider(prov, resolved_style)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)



