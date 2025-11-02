"""
Custom State Colors
Explicitly set icon colors for specific states.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap_icons_fa import FAIcon


def main():
    root = tb.Window(themename="cosmo")
    root.title("Custom State Colors - Stateful Icons")
    root.geometry("500x350")

    # Header
    header = ttk.Label(
        root,
        text="Custom State Colors",
        font=("Segoe UI", 16, "bold"),
        padding=20
    )
    header.pack()

    # Description
    desc = ttk.Label(
        root,
        text="Star changes to custom colors based on state",
        font=("Segoe UI", 10),
        padding=10
    )
    desc.pack()

    # Container
    container = ttk.Frame(root, padding=30)
    container.pack(expand=True)

    # Create star icon
    icon = FAIcon("star", size=48, style="solid")

    # Create button
    button = ttk.Button(container, text="Rate", compound="left", style="warning.TButton")

    # Define custom colors for each state
    icon.map(
        button,
        statespec=[
            ("hover", "#FFD700"),      # Gold on hover
            ("pressed", "#FFA500"),    # Orange when pressed
            ("disabled", "#808080"),   # Grey when disabled
        ]
    )

    button.pack(pady=20)

    # Color legend
    legend_frame = ttk.LabelFrame(root, text="State Colors", padding=15)
    legend_frame.pack(pady=10, padx=40, fill="x")

    ttk.Label(legend_frame, text="• Normal:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=2)
    ttk.Label(legend_frame, text="Theme default", font=("Segoe UI", 9), foreground="gray").grid(row=0, column=1, sticky="w", padx=10)

    ttk.Label(legend_frame, text="• Hover:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=2)
    ttk.Label(legend_frame, text="#FFD700 (Gold)", font=("Segoe UI", 9), foreground="#FFD700").grid(row=1, column=1, sticky="w", padx=10)

    ttk.Label(legend_frame, text="• Pressed:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=2)
    ttk.Label(legend_frame, text="#FFA500 (Orange)", font=("Segoe UI", 9), foreground="#FFA500").grid(row=2, column=1, sticky="w", padx=10)

    ttk.Label(legend_frame, text="• Disabled:", font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", pady=2)
    ttk.Label(legend_frame, text="#808080 (Grey)", font=("Segoe UI", 9), foreground="#808080").grid(row=3, column=1, sticky="w", padx=10)

    # Disabled button example
    icon2 = FAIcon("star", size=32, style="solid")
    btn_disabled = ttk.Button(container, text="Disabled", compound="left", state="disabled", style="warning.TButton")
    icon2.map(
        btn_disabled,
        statespec=[
            ("disabled", "#808080"),
        ]
    )
    btn_disabled.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()