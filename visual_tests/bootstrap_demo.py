import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons import BootstrapIcon


def main():
    root = tk.Tk()
    root.title("Bootstrap Icons Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    icon0 = BootstrapIcon("house", size=64)
    ttk.Label(root, text="default", image=icon0.image, compound="left").pack(**opts)

    icon1 = BootstrapIcon("house", style="outline", size=64)
    ttk.Label(root, text="outline (style)", image=icon1.image, compound="left").pack(**opts)

    icon2 = BootstrapIcon("house-outline", size=64)
    ttk.Label(root, text="outline (name)", image=icon2.image, compound="left").pack(**opts)

    icon3 = BootstrapIcon("house", style="fill", size=64)
    ttk.Label(root, text="fill (style)", image=icon3.image, compound="left").pack(**opts)

    icon4 = BootstrapIcon("house-fill", size=64)
    ttk.Label(root, text="fill (name)", image=icon4.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

