import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_fluent import FluentIcon


def main():
    root = tk.Tk()
    root.title("Fluent System Icons Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    r = FluentIcon("home-16", size=64, style="regular")
    ttk.Label(root, text="regular", image=r.image, compound="left").pack(**opts)

    f = FluentIcon("home-16", size=64, style="filled")
    ttk.Label(root, text="filled", image=f.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

