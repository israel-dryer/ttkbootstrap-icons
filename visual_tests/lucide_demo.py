import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_lucide import LucideIcon


def main():
    root = tk.Tk()
    root.title("Lucide Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    i0 = LucideIcon("house", size=64, color="#333")
    ttk.Label(root, text="house", image=i0.image, compound="left").pack(**opts)

    i1 = LucideIcon("heart", size=64, color="#e03131")
    ttk.Label(root, text="heart", image=i1.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

