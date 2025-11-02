"""
Basic Automatic Color Mapping
Icons automatically inherit the parent style's foreground colors for each state.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap_icons_fa import FAIcon


def main():
    root = tb.Window(themename="darkly")
    root.title("Automatic Color Mapping - Stateful Icons")
    root.geometry("400x300")

    # Header
    header = ttk.Label(
        root,
        text="Automatic Color Mapping",
        font=("Segoe UI", 16, "bold"),
        padding=20
    )
    header.pack()

    # Description
    desc = ttk.Label(
        root,
        text="Icons automatically match theme colors\nHover and click to see state changes",
        font=("Segoe UI", 10),
        justify="center",
        padding=10
    )
    desc.pack()

    # Container
    container = ttk.Frame(root, padding=40)
    container.pack(expand=True)

    # Create an icon
    icon = FAIcon("heart", size=32, style="solid")

    # Create a button
    btn = ttk.Button(container, text="Like", compound="left", style="primary.TButton")

    # Map the icon to the button - colors auto-match the theme
    icon.map(btn)

    btn.pack(padx=20, pady=20)

    # Instructions
    instructions = ttk.Label(
        root,
        text="The icon color automatically follows the button's theme colors",
        font=("Segoe UI", 9),
        foreground="gray",
        padding=10
    )
    instructions.pack(side="bottom")

    root.mainloop()


if __name__ == "__main__":
    main()