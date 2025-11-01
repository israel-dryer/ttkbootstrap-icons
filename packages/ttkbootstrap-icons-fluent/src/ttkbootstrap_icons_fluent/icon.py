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


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Fluent Icons")
    root.minsize(300, 200)
    options = {"fill": "x", "padx": 10, "pady": 10}

    # using the default style
    icon0 = FluentIcon("add-12", size=64)
    ttk.Label(root, text="default style", image=icon0.image, compound="left").pack(**options)

    # using the style parameter
    icon1 = FluentIcon("add-square-20", style="filled", size=64)
    ttk.Label(root, text="filled with style param", image=icon1.image, compound="left").pack(**options)

    icon1_1 = FluentIcon("add-square-20-filled", size=64)
    ttk.Label(root, text="filled with style in name", image=icon1_1.image, compound="left").pack(**options)

    # using the style in name
    icon2 = FluentIcon("settings-16-regular", size=64)
    ttk.Label(root, text="regular with style in name", image=icon2.image, compound="left").pack(**options)

    # using the style in name
    icon2 = FluentIcon("ic-fluent-cube-16-regular", size=64)
    ttk.Label(root, text="regular with style in name", image=icon2.image, compound="left").pack(**options)

    # using the style parameter
    icon3 = FluentIcon("settings-16", style="regular", size=64)
    ttk.Label(root, text="regular with style param", image=icon3.image, compound="left").pack(**options)

    # using the style in name
    icon4 = FluentIcon("save-32-light", size=64)
    ttk.Label(root, text="light with style in name", image=icon4.image, compound="left").pack(**options)

    # using the style parameter
    icon5 = FluentIcon("ic-fluent-save-32", style="light", size=64)
    ttk.Label(root, text="light with style param", image=icon5.image, compound="left").pack(**options)

    root.mainloop()
