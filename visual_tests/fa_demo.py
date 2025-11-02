import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_fa import FAIcon


def main():
    root = tk.Tk()
    root.title("Font Awesome Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    i0 = FAIcon("house", size=64, style="solid")
    ttk.Label(root, text="solid: house", image=i0.image, compound="left").pack(**opts)

    i1 = FAIcon("bell", size=64, style="regular")
    ttk.Label(root, text="regular: bell", image=i1.image, compound="left").pack(**opts)

    i2 = FAIcon("square-x-twitter", size=64, style="brands")
    ttk.Label(root, text="brands", image=i2.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

