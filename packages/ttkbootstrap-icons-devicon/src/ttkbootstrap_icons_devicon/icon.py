from typing import Literal

from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_devicon.provider import DeviconProvider

DevStyles = Literal['plain', 'plain-wordmark', 'original', 'original-wordmark']


class DevIcon(Icon):
    """Convenience icon for the Devicon glyph set.

    Resolves the provided name (optionally with a style) using `DeviconProvider`,
    then initializes the base `Icon` with the resolved glyph.

    Args:
        name: Glyph name. May be a friendly name (e.g. "anaconda") or a raw glyph
            (e.g. "anaconda-plain"). If you pass a conflicting style (e.g. name ends
            with "-plain" but you set `style="original"`), a `ValueError` is raised.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").
        style: Optional style override: "plain", "original", "plain-wordmark", "original-wordmark". If omitted, the
            provider's default style is used. When `name` already encodes a style suffix (e.g. "-plain"), that suffix
            takes precedence.

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", style: DevStyles | None = None):
        prov = DeviconProvider()
        DevIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, style)
        super().__init__(resolved, size, color)


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Devicon Icons")
    root.minsize(300, 200)
    options = {"fill": "x", "padx": 10, "pady": 10}

    # using the default style
    icon0 = DevIcon("anaconda", size=64)
    ttk.Label(root, text="default style", image=icon0.image, compound="left").pack(**options)

    # using the style parameter
    icon1 = DevIcon("anaconda", style="plain", size=64)
    ttk.Label(root, text="plain with style param", image=icon1.image, compound="left").pack(**options)

    # using the style in name
    icon2 = DevIcon("anaconda-plain", size=64)
    ttk.Label(root, text="plain with style in name", image=icon2.image, compound="left").pack(**options)

    # using the style parameter
    icon3 = DevIcon("anaconda", style="plain-wordmark", size=64)
    ttk.Label(root, text="plain-wordmark with style param", image=icon3.image, compound="left").pack(**options)

    # using the style in name
    icon4 = DevIcon("anaconda-plain-wordmark", size=64)
    ttk.Label(root, text="plain-wordmark with style in name", image=icon4.image, compound="left").pack(**options)

    # using the style parameter
    icon5 = DevIcon("anaconda", style="original", size=64)
    ttk.Label(root, text="original with style param", image=icon5.image, compound="left").pack(**options)

    # using the style in name
    icon6 = DevIcon("anaconda-original", size=64)
    ttk.Label(root, text="original with style in name", image=icon6.image, compound="left").pack(**options)

    # using the style parameter
    icon7 = DevIcon("anaconda", style="original-wordmark", size=64)
    ttk.Label(root, text="original-wordmark with style param", image=icon7.image, compound="left").pack(**options)

    # using the style in name
    icon8 = DevIcon("anaconda-original-wordmark", size=64)
    ttk.Label(root, text="original-wordmark with style in name", image=icon8.image, compound="left").pack(**options)

    root.mainloop()
