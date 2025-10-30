from typing import Literal

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_mat.provider import MaterialProvider

MatStyles = Literal['fill', 'outline']


class MatIcon(Icon):
    """Convenience icon for the Mat Icon glyph set.

    Resolves the provided name (optionally with a style) using `MatProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name. May be a friendly name (e.g. "bell") or a raw glyph
            (e.g. "bell-outline"). If you pass a conflicting style (e.g. name ends
            with "-outline" but you set `style="fill"`), a `ValueError` is raised.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").
        style: Optional style override: "fill", "outline". If omitted, the provider's default style is used.
            When `name` already encodes a style suffix (e.g. "-outline"), that suffix takes precedence.

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", style: MatStyles | None = None):
        prov = MaterialProvider()
        MatIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Material Design Icons")
    root.minsize(300, 200)
    options = {"fill": "x", "padx": 10, "pady": 10}

    # using the default style
    icon0 = MatIcon("bell")
    ttk.Label(root, text="default style", image=icon0.image, compound="left").pack(**options)

    # using the style parameter
    icon1 = MatIcon("bell", style="fill")
    ttk.Label(root, text="fill with style param", image=icon1.image, compound="left").pack(**options)

    # using style in name
    icon4 = MatIcon("bell-fill")
    ttk.Label(root, text="fill with style in name", image=icon4.image, compound="left").pack(**options)

    # using the style in name
    icon3 = MatIcon("bell-outline")
    ttk.Label(root, text="outline with style in name", image=icon3.image, compound="left").pack(**options)

    # using the style parameter
    icon4 = MatIcon("bell", style="outline")
    ttk.Label(root, text="outline with style param", image=icon4.image, compound="left").pack(**options)

    root.mainloop()
