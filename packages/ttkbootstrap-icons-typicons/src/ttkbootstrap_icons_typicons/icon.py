from ttkbootstrap_icons_typicons.provider import TypiconsProvider

from ttkbootstrap_icons.icon import Icon


class TypiconsIcon(Icon):
    """Convenience icon for the Typicons glyph set.

    Resolves the provided name using `TypiconsProvider`, then initializes the base `Icon`
    with the resolved glyph name.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", **kwargs):
        prov = TypiconsProvider()
        TypiconsIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, **kwargs)
        super().__init__(resolved, size, color)


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Typicons Icons")
    root.minsize(300, 200)
    options = {"fill": "x", "padx": 10, "pady": 10}

    # using the default style
    icon0 = TypiconsIcon("arrow-down", size=64)
    ttk.Label(root, text="default style", image=icon0.image, compound="left").pack(**options)

    # using the style parameter
    icon1 = TypiconsIcon("arrow-down", style="fill", size=64)
    ttk.Label(root, text="fill with style param", image=icon1.image, compound="left").pack(**options)

    icon1_1 = TypiconsIcon("arrow-down-fill", size=64)
    ttk.Label(root, text="fill with style in name", image=icon1_1.image, compound="left").pack(**options)

    # using the style in name
    icon2 = TypiconsIcon("arrow-down-outline", size=64)
    ttk.Label(root, text="outline with style in name", image=icon2.image, compound="left").pack(**options)

    # using the style parameter
    icon3 = TypiconsIcon("arrow-down", style="outline", size=64)
    ttk.Label(root, text="outline with style param", image=icon3.image, compound="left").pack(**options)

    root.mainloop()
