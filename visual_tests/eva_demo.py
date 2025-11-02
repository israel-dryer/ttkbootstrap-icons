import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_eva import EvaIcon


def main():
    root = tk.Tk()
    root.title("Eva Icons Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    i0 = EvaIcon("activity", size=64, color="#333", style="outline")
    ttk.Label(root, text="outline", image=i0.image, compound="left").pack(**opts)

    i1 = EvaIcon("activity", size=64, color="#333", style="fill")
    lbl = ttk.Label(root, text="fill", compound="left")
    i1.map(lbl, statespec=[("hover", "red")])
    lbl.pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()
