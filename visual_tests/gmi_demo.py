import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_gmi import GMatIcon


def main():
    root = tk.Tk()
    root.title("Google Material Icons Demo")
    root.minsize(360, 280)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    base = GMatIcon("home", 64, "#555", style="baseline")
    outl = GMatIcon("home", 64, "#555", style="outlined")
    rnd = GMatIcon("home", 64, "#555", style="round")
    shp = GMatIcon("home", 64, "#555", style="sharp")
    two = GMatIcon("home", 64, "#555", style="twotone")

    for lbl, ic in [("Baseline", base), ("Outlined", outl), ("Round", rnd), ("Sharp", shp), ("TwoTone", two)]:
        ttk.Label(root, text=lbl, image=ic.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

