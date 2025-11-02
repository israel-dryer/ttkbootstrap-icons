from typing import Literal

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_fluent.provider import FluentSystemFontProvider

FluentStyles = Literal['regular', 'filled', 'light']


class FluentIcon(Icon):
    """Convenience icon for the Fluent Icon glyph set.

    Resolves the provided name (optionally with a style) using `FluentProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name. May be a friendly name (e.g. "settings-16") or a raw glyph
            (e.g. "settings-16-regular"). If you pass a conflicting style (e.g. name ends
            with "-regular" but you set `style="filled"`), a `ValueError` is raised.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").
        style: Optional style override: "filled", "regular", "light". If omitted, the provider's default style is used.
            When `name` already encodes a style suffix (e.g. "-regular"), that suffix takes precedence.

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", style: FluentStyles | None = None):
        prov = FluentSystemFontProvider()
        resolved_style = prov.resolve_icon_style(name, style)
        FluentIcon.initialize_with_provider(prov, resolved_style)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)



