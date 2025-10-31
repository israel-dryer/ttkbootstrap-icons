from typing import Literal

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_remix.provider import RemixProvider

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
        prov = RemixProvider()
        RemixIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Remix Icons")
    root.minsize(300, 200)
    options = {"fill": "x", "padx": 10, "pady": 10}

    # using the default style
    icon0 = RemixIcon("admin")
    ttk.Label(root, text="default style", image=icon0.image, compound="left").pack(**options)

    # using the style parameter
    icon1 = RemixIcon("admin", style="fill")
    ttk.Label(root, text="fill with style param", image=icon1.image, compound="left").pack(**options)

    icon1_1 = RemixIcon("admin-fill")
    ttk.Label(root, text="fill with style in name", image=icon1_1.image, compound="left").pack(**options)

    # using the style in name
    icon2 = RemixIcon("admin-line")
    ttk.Label(root, text="line with style in name", image=icon2.image, compound="left").pack(**options)

    # using the style parameter
    icon3 = RemixIcon("admin", style="line")
    ttk.Label(root, text="line with style param", image=icon3.image, compound="left").pack(**options)

    root.mainloop()
