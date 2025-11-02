import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons_ion import IonIcon


def main():
    root = tk.Tk()
    root.title("Ionicons v2 Demo")
    root.minsize(320, 240)
    opts = {"fill": "x", "padx": 10, "pady": 8}

    i0 = IonIcon("home", size=64, color="#198754")
    ttk.Label(root, text="home", image=i0.image, compound="left").pack(**opts)

    i1 = IonIcon("star", size=64, color="#ffd43b")
    ttk.Label(root, text="star", image=i1.image, compound="left").pack(**opts)

    root.mainloop()


if __name__ == "__main__":
    main()

