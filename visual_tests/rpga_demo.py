import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_rpga import RPGAIcon


def main():
    root = tk.Tk()
    root.title("RPG Awesome Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    i0 = RPGAIcon("sword", size=64, color="#6f42c1")
    ttk.Label(root, text="sword", image=i0.image, compound="left").pack(**opts)

    i1 = RPGAIcon("shield", size=64, color="#343a40")
    ttk.Label(root, text="shield", image=i1.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

