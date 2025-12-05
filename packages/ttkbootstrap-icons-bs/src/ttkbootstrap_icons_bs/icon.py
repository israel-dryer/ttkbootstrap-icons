from __future__ import annotations

"""Bootstrap icon provider and convenience Icon wrapper.

This module exposes:
- `BootstrapIcon`: a convenience wrapper around `Icon` that resolves Bootstrap glyph names.
- `BootstrapProvider`: a `BaseFontProvider` subclass that understands Bootstrap's
  two styles: "outline" and "fill", both backed by the same font file and separated
  via a name predicate (presence of the `-fill` suffix).

Example:
    from tkinter import ttk

    # using the style parameter
    icon1 = BootstrapIcon("house", style="outline")
    ttk.Label(root, text="Home", image=icon1.image, compound="left").pack()

    # using the style in name
    icon2 = BootstrapIcon("house-outline")
    ttk.Label(root, text="Home", image=icon2.image, compound="left").pack()
"""

from typing import Literal

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_bs.provider import BootstrapFontProvider

BootstrapStyles = Literal['outline', 'fill']


class BootstrapIcon(Icon):
    """Convenience icon for the Bootstrap glyph set.

    Resolves the provided name (optionally with a style) using `BootstrapFontProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name. May be a friendly name (e.g. "house") or a raw glyph
            (e.g. "house-fill"). If you pass a conflicting style (e.g. name ends
            with "-fill" but you set `style="outline"`), a `ValueError` is raised.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").
        style: Optional style override: "outline" or "fill". If omitted, the
            provider's default style is used. When `name` already encodes a
            style suffix (e.g. "-fill"), that suffix takes precedence.

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", style: BootstrapStyles | None = None):
        prov = BootstrapFontProvider()
        BootstrapIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)