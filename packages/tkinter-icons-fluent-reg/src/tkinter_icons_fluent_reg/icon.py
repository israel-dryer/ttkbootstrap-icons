from __future__ import annotations

from tkinter_icons.icon import Icon
from tkinter_icons.render import RenderOptions
from tkinter_icons_fluent_reg.provider import FluentRegularFontProvider


class FluentRegularIcon(Icon):
    """Convenience icon for the Fluent System Icons (Regular style only).

    Resolves the provided name using `FluentRegularFontProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name. May be a friendly name (e.g. "settings-16") or a raw glyph
            (e.g. "settings-16-regular").
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").

    Raises:
        ValueError: If the name cannot be resolved.
    """

    provider_class = FluentRegularFontProvider

    def __init__(self, name: str, size: int = 24, color: str = "black",
                 *, options: RenderOptions | None = None):
        prov = FluentRegularFontProvider()
        FluentRegularIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name)
        super().__init__(resolved, size, color, options=options)