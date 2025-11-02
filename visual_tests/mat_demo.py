import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_mat import MatIcon


def main():
    root = tk.Tk()
    root.title("MDI Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    i0 = MatIcon("home", size=64, color="#dc3545")
    ttk.Label(root, text="home", image=i0.image, compound="left").pack(**opts)

    i1 = MatIcon("account", size=64, color="#339af0")
    ttk.Label(root, text="account", image=i1.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

