import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_simple import SimpleIcon


def main():
    root = tk.Tk()
    root.title("Simple Icons Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    i0 = SimpleIcon("python", size=64, color="#333333")
    ttk.Label(root, text="python", image=i0.image, compound="left").pack(**opts)

    i1 = SimpleIcon("github", size=64, color="#333333")
    ttk.Label(root, text="github", image=i1.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

