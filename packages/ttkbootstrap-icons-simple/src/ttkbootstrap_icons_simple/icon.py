from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_simple.provider import SimpleProvider


class SimpleIcon(Icon):
    """Convenience icon for the Simple Icon glyph set.

    Args:
        name: glyph name.
        size: Pixel size of the rasterized image (default: 24).
        color: Foreground color used to render the glyph (default: "black").

    Raises:
        ValueError: If the name cannot be resolved for the requested style.
    """

    def __init__(self, name: str, size: int = 24, color: str = "black", **kwargs):
        prov = SimpleProvider()
        SimpleIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, **kwargs)
        super().__init__(resolved, size, color)


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Simple Icons")
    root.minsize(300, 200)
    options = {"fill": "x", "padx": 10, "pady": 10}

    # using the default style
    icon0 = SimpleIcon("alchemy", size=64)
    ttk.Label(root, text="default style", image=icon0.image, compound="left").pack(**options)

    root.mainloop()
