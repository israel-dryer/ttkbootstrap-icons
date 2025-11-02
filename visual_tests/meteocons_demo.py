import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_meteocons import MeteoIcon


def main():
    root = tk.Tk()
    root.title("Meteocons Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    i0 = MeteoIcon("a", size=64)
    ttk.Label(root, text="sample", image=i0.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

