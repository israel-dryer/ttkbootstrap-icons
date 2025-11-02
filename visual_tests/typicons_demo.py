import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_typicons import TypiconsIcon


def main():
    root = tk.Tk()
    root.title("Typicons Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    i0 = TypiconsIcon("arrow-down", size=64)
    ttk.Label(root, text="default", image=i0.image, compound="left").pack(**opts)

    i1 = TypiconsIcon("arrow-down", style="fill", size=64)
    ttk.Label(root, text="fill (style)", image=i1.image, compound="left").pack(**opts)

    i2 = TypiconsIcon("arrow-down-outline", size=64)
    ttk.Label(root, text="outline (name)", image=i2.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

