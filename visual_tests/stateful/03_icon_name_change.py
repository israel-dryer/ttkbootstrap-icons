"""
Change Icon Name Per State
Display entirely different icons for different states.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap_icons_fa import FAIcon


def main():
    root = tb.Window(themename="cosmo")
    root.title("Icon Name Change - Stateful Icons")
    root.geometry("500x350")

    # Header
    header = ttk.Label(
        root,
        text="Icon Name Change on State",
        font=("Segoe UI", 16, "bold"),
        padding=20
    )
    header.pack()

    # Description
    desc = ttk.Label(
        root,
        text="Bookmark switches from regular to solid on hover\nand changes color when pressed",
        font=("Segoe UI", 10),
        justify="center",
        padding=10
    )
    desc.pack()

    # Container
    container = ttk.Frame(root, padding=30)
    container.pack(expand=True)

    # Create bookmark icon (regular style)
    icon = FAIcon("bookmark", size=48, style="regular")

    # Create button
    button = ttk.Button(container, text="Save for Later", compound="left", style="info.TButton")

    # Switch to filled bookmark on hover with color changes
    icon.map(
        button,
        statespec=[
            ("hover", {"name": "bookmark", "color": "#007bff"}),
            ("pressed", {"name": "bookmark", "color": "#0056b3"}),
        ]
    )

    button.pack(pady=20)

    # Info panel
    info_frame = ttk.LabelFrame(root, text="State Behavior", padding=15)
    info_frame.pack(pady=10, padx=40, fill="x")

    ttk.Label(
        info_frame,
        text="• Normal: Regular outline bookmark (default color)",
        font=("Segoe UI", 9),
        justify="left"
    ).pack(anchor="w", pady=2)

    ttk.Label(
        info_frame,
        text="• Hover: Filled bookmark with blue color (#007bff)",
        font=("Segoe UI", 9),
        justify="left"
    ).pack(anchor="w", pady=2)

    ttk.Label(
        info_frame,
        text="• Pressed: Filled bookmark with darker blue (#0056b3)",
        font=("Segoe UI", 9),
        justify="left"
    ).pack(anchor="w", pady=2)

    # Additional example button
    ttk.Label(root, text="Compare with normal button:", font=("Segoe UI", 9), foreground="gray").pack(pady=(20, 5))
    normal_btn = ttk.Button(root, text="No State Mapping", style="info.TButton")
    normal_btn.pack()

    root.mainloop()


if __name__ == "__main__":
    main()