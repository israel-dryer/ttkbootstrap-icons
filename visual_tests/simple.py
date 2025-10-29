import tkinter as tk
from tkinter import ttk
import random

from ttkbootstrap_icons_simple import SimpleIcon
from ttkbootstrap_icons_simple.provider import SimpleFontProvider


def main():
    random.seed()
    app = tk.Tk()
    app.title("Simple Icons")

    prov = SimpleFontProvider()
    idx = prov.build_display_index()
    names = idx.get("names", [])

    frame = ttk.LabelFrame(app, text="default")
    frame.pack(padx=10, pady=10, fill="x", expand=True)

    if names:
        a = SimpleIcon(random.choice(names))
        ttk.Label(frame, image=a.image, compound="left", text="default").pack(padx=10, pady=10, side="left")

    app.mainloop()


if __name__ == "__main__":
    main()

