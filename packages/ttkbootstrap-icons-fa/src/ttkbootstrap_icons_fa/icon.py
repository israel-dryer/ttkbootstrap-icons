from typing import Literal

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_fa.provider import FAProvider

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
        style: Optional style override: "regular", "solid", "brands". If omitted, the provider's default
        style is used.

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", style: FAStyles | None = None):
        prov = FAProvider()
        # Resolve the style from the name if not explicitly provided
        resolved_style = prov.resolve_icon_style(name, style)
        FAIcon.initialize_with_provider(prov, resolved_style)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Font Awesome Icons Demo")
    root.minsize(400, 250)
    options = {"fill": "x", "padx": 10, "pady": 5}

    # Default style
    icon0 = FAIcon("anchor", size=64)
    ttk.Label(root, text="Default (baseline)", image=icon0.image, compound="left").pack(**options)

    # Using style parameter
    icon1 = FAIcon("anchor", style="solid", size=64)
    ttk.Label(root, text="Solid (via style param)", image=icon1.image, compound="left").pack(**options)

    # Using style in name
    icon2 = FAIcon("anchor-solid", size=64)
    ttk.Label(root, text="Solid (via name suffix)", image=icon2.image, compound="left").pack(**options)

    # Using style in name
    icon2 = FAIcon("address-card-regular", size=64)
    ttk.Label(root, text="Regular (via name suffix)", image=icon2.image, compound="left").pack(**options)

    icon3 = FAIcon("address-card", style="regular", size=64)
    ttk.Label(root, text="Regular (via style param)", image=icon3.image, compound="left").pack(**options)

    # Using style in name
    icon4 = FAIcon("asterisk-brands", size=64)
    ttk.Label(root, text="Brand (via name suffix)", image=icon4.image, compound="left").pack(**options)

    icon5 = FAIcon("asterisk", style="brands", size=64)
    ttk.Label(root, text="Brand (via style param)", image=icon5.image, compound="left").pack(**options)

    root.mainloop()
