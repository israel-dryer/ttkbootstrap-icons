"""
All States Visual Reference
Comprehensive display of all common TTK states for documentation.
"""
import tkinter as tk


import ttkbootstrap as tb
from ttkbootstrap_icons_fa import FAIcon


def main():
    root = tb.Window(themename="cosmo")
    root.title("TTK State Reference - Stateful Icons")
    root.geometry("700x600")

    # Header
    header = tb.Label(
        root,
        text="TTK State Flags Reference",
        font=("Segoe UI", 16, "bold"),
        padding=20
    )
    header.pack()

    # Description
    desc = tb.Label(
        root,
        text="Visual reference of common TTK state flags with icons",
        font=("Segoe UI", 10),
        padding=10
    )
    desc.pack()

    # Main container with grid
    container = tb.Frame(root, padding=20)
    container.pack(fill="both", expand=True)

    # Headers
    tb.Label(container, text="State", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    tb.Label(container, text="Example", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, padx=10, pady=5)
    tb.Label(container, text="Description", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")

    row = 1

    # Normal state
    tb.Label(container, text="normal", font=("Segoe UI", 9)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    icon1 = FAIcon("circle", size=24, style="solid")
    btn1 = tb.Button(container, text="Normal", compound="left")
    icon1.map(btn1)
    btn1.grid(row=row, column=1, padx=10, pady=5)
    tb.Label(container, text="Default state", font=("Segoe UI", 9), bootstyle="secondary").grid(row=row, column=2, padx=10, pady=5, sticky="w")
    row += 1

    # Hover state
    tb.Label(container, text="hover", font=("Segoe UI", 9)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    tb.Label(container, text="(hover over button)", font=("Segoe UI", 8), bootstyle="secondary").grid(row=row, column=1, padx=10, pady=5)
    tb.Label(container, text="Mouse over widget", font=("Segoe UI", 9), bootstyle="secondary").grid(row=row, column=2, padx=10, pady=5, sticky="w")
    row += 1

    # Pressed state
    tb.Label(container, text="pressed", font=("Segoe UI", 9)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    tb.Label(container, text="(click and hold)", font=("Segoe UI", 8), bootstyle="secondary").grid(row=row, column=1, padx=10, pady=5)
    tb.Label(container, text="Widget being clicked", font=("Segoe UI", 9), bootstyle="secondary").grid(row=row, column=2, padx=10, pady=5, sticky="w")
    row += 1

    # Disabled state
    tb.Label(container, text="disabled", font=("Segoe UI", 9)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    icon2 = FAIcon("circle", size=24, style="solid")
    btn2 = tb.Button(container, text="Disabled", compound="left", state="disabled")
    icon2.map(btn2, statespec=[("disabled", "#808080")])
    btn2.grid(row=row, column=1, padx=10, pady=5)
    tb.Label(container, text="Widget is disabled", font=("Segoe UI", 9), bootstyle="secondary").grid(row=row, column=2, padx=10, pady=5, sticky="w")
    row += 1

    # Selected state (Checkbutton)
    tb.Label(container, text="selected", font=("Segoe UI", 9)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    icon3 = FAIcon("check-circle", size=24, style="solid")
    check_var = tk.BooleanVar(value=True)
    check = tb.Checkbutton(container, text="Selected", variable=check_var, bootstyle="success-toolbutton")
    icon3.map(check, statespec=[("selected", "#28a745"), ("!selected", "#6c757d")])
    check.grid(row=row, column=1, padx=10, pady=5)
    tb.Label(container, text="Checkbutton/Radiobutton checked", font=("Segoe UI", 9), bootstyle="secondary").grid(row=row, column=2, padx=10, pady=5, sticky="w")
    row += 1

    # Active state
    tb.Label(container, text="active", font=("Segoe UI", 9)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    icon4 = FAIcon("star", size=24, style="solid")
    btn4 = tb.Button(container, text="Active", compound="left")
    btn4.state(['active'])
    icon4.map(btn4, statespec=[("active", "#ffc107")])
    btn4.grid(row=row, column=1, padx=10, pady=5)
    tb.Label(container, text="Widget has focus/is active", font=("Segoe UI", 9), bootstyle="secondary").grid(row=row, column=2, padx=10, pady=5, sticky="w")
    row += 1

    # Focus state
    tb.Label(container, text="focus", font=("Segoe UI", 9)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    tb.Label(container, text="(tab to focus)", font=("Segoe UI", 8), bootstyle="secondary").grid(row=row, column=1, padx=10, pady=5)
    tb.Label(container, text="Widget has keyboard focus", font=("Segoe UI", 9), bootstyle="secondary").grid(row=row, column=2, padx=10, pady=5, sticky="w")
    row += 1

    # Negation example
    tb.Label(container, text="!disabled", font=("Segoe UI", 9)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    icon5 = FAIcon("circle", size=24, style="solid")
    btn5 = tb.Button(container, text="Not Disabled", compound="left")
    icon5.map(btn5, statespec=[("!disabled", "#007bff")])
    btn5.grid(row=row, column=1, padx=10, pady=5)
    tb.Label(container, text="NOT in disabled state", font=("Segoe UI", 9), bootstyle="secondary").grid(row=row, column=2, padx=10, pady=5, sticky="w")
    row += 1

    # Combined states example
    row += 1
    tb.Separator(container, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=10)
    row += 1

    tb.Label(container, text="Combined States:", font=("Segoe UI", 10, "bold"), foreground="#007bff").grid(row=row, column=0, columnspan=3, sticky="w", padx=10, pady=5)
    row += 1

    # Hover + Not disabled
    tb.Label(container, text="hover !disabled", font=("Segoe UI", 9)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    tb.Label(container, text="(hover to see)", font=("Segoe UI", 8), bootstyle="secondary").grid(row=row, column=1, padx=10, pady=5)
    tb.Label(container, text="Hover AND not disabled", font=("Segoe UI", 9), bootstyle="secondary").grid(row=row, column=2, padx=10, pady=5, sticky="w")
    row += 1

    # Selected + Active
    tb.Label(container, text="selected active", font=("Segoe UI", 9)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    icon6 = FAIcon("toggle-on", size=24, style="solid")
    check2_var = tk.BooleanVar(value=True)
    check2 = tb.Checkbutton(container, text="Selected & Active", variable=check2_var, bootstyle="info-toolbutton")
    check2.state(['active'])
    icon6.map(check2, statespec=[("selected active", "#17a2b8")])
    check2.grid(row=row, column=1, padx=10, pady=5)
    tb.Label(container, text="Selected AND active", font=("Segoe UI", 9), bootstyle="secondary").grid(row=row, column=2, padx=10, pady=5, sticky="w")

    # Instructions
    instructions = tb.Label(
        root,
        text="Interact with widgets to see different state combinations",
        font=("Segoe UI", 9),
        bootstyle="secondary",
        padding=10
    )
    instructions.pack(side="bottom")

    root.mainloop()


if __name__ == "__main__":
    main()