import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_devicon import DevIcon


def main():
    root = tk.Tk()
    root.title("Devicon Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    i0 = DevIcon("python-plain", size=64)
    ttk.Label(root, text="plain", image=i0.image, compound="left").pack(**opts)

    i1 = DevIcon("python", style="original", size=64)
    ttk.Label(root, text="original (style)", image=i1.image, compound="left").pack(**opts)

    i2 = DevIcon("python-original-wordmark", size=64)
    ttk.Label(root, text="original-wordmark (name)", image=i2.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

