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
from ttkbootstrap_icons.providers import BaseFontProvider

BootstrapStyles = Literal['outline', 'fill']


class BootstrapIcon(Icon):
    """Convenience icon for the Bootstrap glyph set.

    Resolves the provided name (optionally with a style) using `BootstrapProvider`,
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
        prov = BootstrapProvider()
        BootstrapIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)


class BootstrapProvider(BaseFontProvider):
    """Provider for the Bootstrap Icons dataset.

    Bootstrap ships two styles—"outline" and "fill"—encoded by the presence of a
    ``-fill`` suffix in the raw glyph name. Both styles share the same font file
    and are separated via a predicate per style.

    Attributes:
        name: Provider identifier ("bootstrap").
        display_name: Human-friendly name ("Bootstrap").
        default_style: Default style ("outline").
        styles: Map of style → {filename, predicate}.
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
            display_name="Bootstrap",
            package="ttkbootstrap_icons.assets",
            default_style="outline",
            styles={
                "fill": {"filename": "bootstrap.ttf", "predicate": BootstrapProvider._is_fill_style},
                "outline": {"filename": "bootstrap.ttf", "predicate": BootstrapProvider._is_outline_style},
            }
        )

    @staticmethod
    def _is_outline_style(name: str) -> bool:
        return '-fill' not in name

    @staticmethod
    def _is_fill_style(name: str) -> bool:
        return '-fill' in name

    @staticmethod
    def format_glyph_name(glyph_name: str) -> str:
        """Display friendly name for font name"""
        return str(glyph_name).lower().replace('-fill', '')


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Bootstrap Icons")
    root.minsize(300, 200)
    options = {"fill": "x", "padx": 10, "pady": 10}

    # using the default style
    icon0 = BootstrapIcon("house")
    ttk.Label(root, text="default style", image=icon0.image, compound="left").pack(**options)

    # using the style parameter
    icon1 = BootstrapIcon("house", style="outline")
    ttk.Label(root, text="outline with style param", image=icon1.image, compound="left").pack(**options)

    # using the style in name
    icon2 = BootstrapIcon("house-outline")
    ttk.Label(root, text="outline wit style in name", image=icon2.image, compound="left").pack(**options)

    # using the style parameter
    icon3 = BootstrapIcon("house", style="fill")
    ttk.Label(root, text="fill with style param", image=icon3.image, compound="left").pack(**options)

    # using the style in name
    icon4 = BootstrapIcon("house-fill")
    ttk.Label(root, text="fill with style in name", image=icon4.image, compound="left").pack(**options)

    root.mainloop()
