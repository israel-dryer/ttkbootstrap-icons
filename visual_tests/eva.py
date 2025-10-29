import tkinter as tk
from tkinter import ttk
import random

from ttkbootstrap_icons_eva import EvaIcon
from ttkbootstrap_icons_eva.provider import EvaFontProvider


def main():
    random.seed()
    app = tk.Tk()
    app.title("Eva Icons styles")

    prov = EvaFontProvider()
    idx = prov.build_display_index()
    styles = idx.get("styles", []) or [prov.get_default_style() or "fill"]
    default_style = prov.get_default_style() or (styles[0] if styles else "fill")

    keepalive = []

    for style in styles:
        frame = ttk.LabelFrame(app, text=str(style))
        frame.pack(padx=10, pady=10, fill="x", expand=True)

        names = idx.get("display_names_by_style", {}).get(style) or idx.get("names", [])
        if not names:
            continue
        name = random.choice(names)

        if style == default_style:
            a1 = EvaIcon(name)
            ttk.Label(frame, image=a1.image, compound="left", text="default (no style)").pack(padx=10, pady=10, side="left")
            keepalive.append(a1)

        a2 = EvaIcon(name, style=style)
        ttk.Label(frame, image=a2.image, compound="left", text="style as property").pack(padx=10, pady=10, side="left")
        keepalive.append(a2)

        a3 = EvaIcon(f"{name}-{style}")
        ttk.Label(frame, image=a3.image, compound="left", text="style as name").pack(padx=10, pady=10, side="left")
        keepalive.append(a3)

    app.mainloop()


if __name__ == "__main__":
    main()

