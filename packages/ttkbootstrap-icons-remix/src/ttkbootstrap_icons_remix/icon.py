from typing import Literal

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_remix.provider import RemixFontProvider

RemixStyles = Literal['fill', 'line']


class RemixIcon(Icon):
    """Convenience icon for the Remix Icon glyph set.

    Resolves the provided name (optionally with a style) using `RemixProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name. May be a friendly name (e.g. "admin") or a raw glyph
            (e.g. "admin-line"). If you pass a conflicting style (e.g. name ends
            with "-line" but you set `style="fill"`), a `ValueError` is raised.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").
        style: Optional style override: "fill", "line". If omitted, the provider's default style is used.
            When `name` already encodes a style suffix (e.g. "-line"), that suffix takes precedence.

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", style: RemixStyles | None = None):
        prov = RemixFontProvider()
        RemixIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)



