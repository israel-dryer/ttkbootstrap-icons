"""
State Comparison Visual
Shows all button states side by side for documentation screenshots.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap_icons_fa import FAIcon


def main():
    root = tb.Window(themename="cosmo")
    root.title("State Comparison - Stateful Icons")
    root.geometry("600x400")

    # Header
    header = ttk.Label(
        root,
        text="Button State Comparison",
        font=("Segoe UI", 16, "bold"),
        padding=20
    )
    header.pack()

    # Container frame
    container = ttk.Frame(root, padding=20)
    container.pack(fill="both", expand=True)

    # Normal state
    ttk.Label(container, text="Normal State:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=5)
    icon1 = FAIcon("heart", size=32, style="solid")
    btn1 = ttk.Button(container, text="Like", compound="left", style="primary.TButton")
    icon1.map(btn1)
    btn1.grid(row=0, column=1, padx=20, pady=5)

    # Hover state (simulated with label)
    ttk.Label(container, text="Hover State:", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w", pady=5)
    ttk.Label(container, text="(Move mouse over button to see)", foreground="gray").grid(row=2, column=0, sticky="w")

    # Pressed state (simulated)
    ttk.Label(container, text="Pressed State:", font=("Segoe UI", 11, "bold")).grid(row=3, column=0, sticky="w", pady=5)
    ttk.Label(container, text="(Click and hold to see)", foreground="gray").grid(row=4, column=0, sticky="w")

    # Disabled state
    ttk.Label(container, text="Disabled State:", font=("Segoe UI", 11, "bold")).grid(row=5, column=0, sticky="w", pady=5)
    icon2 = FAIcon("heart", size=32, style="solid")
    btn2 = ttk.Button(container, text="Like", compound="left", state="disabled", style="primary.TButton")
    icon2.map(btn2)
    btn2.grid(row=5, column=1, padx=20, pady=5)

    # Info label
    info = ttk.Label(
        root,
        text="Hover over and click the top button to see state changes",
        font=("Segoe UI", 9),
        foreground="gray",
        padding=10
    )
    info.pack(side="bottom")

    root.mainloop()


if __name__ == "__main__":
    main()