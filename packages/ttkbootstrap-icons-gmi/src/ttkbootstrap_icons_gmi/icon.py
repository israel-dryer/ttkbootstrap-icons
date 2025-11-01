from typing import Literal

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_gmi.provider import GMIProvider

GMIStyles = Literal['baseline', 'outlined', 'round', 'sharp']


class GMIIcon(Icon):
    """Convenience icon for the GMI Icon glyph set.

    Resolves the provided name (optionally with a style) using `GMIProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name. May be a friendly name (e.g. "home") or a raw glyph
            (e.g. "home-outlined"). If you pass a conflicting style (e.g. name ends
            with "-outlined" but you set `style="round"`), a `ValueError` is raised.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").
        style: Optional style override: "baseline", "outlined", "round", "sharp". If omitted, the provider's default
        style is used.

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", style: GMIStyles | None = None):
        prov = GMIProvider()
        # Resolve the style from the name if not explicitly provided
        resolved_style = prov.resolve_icon_style(name, style)
        GMIIcon.initialize_with_provider(prov, resolved_style)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("GMI Icons Demo")
    root.minsize(400, 250)
    options = {"fill": "x", "padx": 10, "pady": 5}

    # Default style
    icon0 = GMIIcon("home", size=64)
    ttk.Label(root, text="Default (baseline)", image=icon0.image, compound="left").pack(**options)

    # Using style parameter
    icon1 = GMIIcon("home", style="outlined", size=64)
    ttk.Label(root, text="Outlined (via style param)", image=icon1.image, compound="left").pack(**options)

    # Using style in name
    icon2 = GMIIcon("home-outlined", size=64)
    ttk.Label(root, text="Round (via name suffix)", image=icon2.image, compound="left").pack(**options)

    # Using style in name
    icon2 = GMIIcon("home-round", size=64)
    ttk.Label(root, text="Round (via name suffix)", image=icon2.image, compound="left").pack(**options)

    icon3 = GMIIcon("home", style="sharp", size=64)
    ttk.Label(root, text="Sharp (via style param)", image=icon3.image, compound="left").pack(**options)

    root.mainloop()
