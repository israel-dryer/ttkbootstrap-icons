import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_remix import RemixIcon


def main():
    root = tk.Tk()
    root.title("Remix Icon Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    i0 = RemixIcon("home-3-line", size=64, color="#fd7e14")
    ttk.Label(root, text="line", image=i0.image, compound="left").pack(**opts)

    i1 = RemixIcon("home-3-fill", size=64, color="#fd7e14")
    ttk.Label(root, text="fill", image=i1.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

