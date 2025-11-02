"""
Multi-State Button with Complex Interactions
Combine multiple states for rich interaction feedback.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap_icons_fa import FAIcon


def main():
    root = tb.Window(themename="cosmo")
    root.title("Multi-State Button - Stateful Icons")
    root.geometry("550x450")

    # Header
    header = ttk.Label(
        root,
        text="Multi-State Complex Interactions",
        font=("Segoe UI", 16, "bold"),
        padding=20
    )
    header.pack()

    # Description
    desc = ttk.Label(
        root,
        text="Interact with the button to see different state colors\nTry hover, click, and disable states",
        font=("Segoe UI", 10),
        justify="center",
        padding=10
    )
    desc.pack()

    # Container
    container = ttk.Frame(root, padding=30)
    container.pack(expand=True)

    # Download button with complex state mapping
    icon = FAIcon("download", size=32, style="solid")
    download_btn = ttk.Button(
        container,
        text="Download File",
        compound="left",
        style="success.TButton"
    )

    icon.map(
        download_btn,
        statespec=[
            ("pressed", {"color": "#155724"}),           # Dark green when clicked
            ("hover !disabled", {"color": "#1e7e34"}),   # Medium green on hover
            ("disabled", {"color": "#6c757d"}),          # Grey when disabled
            ("!disabled !hover !pressed", {"color": "#28a745"}),  # Default green
        ]
    )

    download_btn.pack(pady=20)

    # Control panel
    control_frame = ttk.LabelFrame(container, text="Controls", padding=15)
    control_frame.pack(pady=20, fill="x")

    # Toggle button state
    enabled_var = tk.BooleanVar(value=True)

    def toggle_button_state():
        if enabled_var.get():
            download_btn.configure(state="normal")
        else:
            download_btn.configure(state="disabled")

    ttk.Checkbutton(
        control_frame,
        text="Enable Download Button",
        variable=enabled_var,
        command=toggle_button_state,
        style="success.Roundtoggle.Toolbutton"
    ).pack(anchor="w", pady=5)

    # Download counter
    download_count = tk.IntVar(value=0)
    count_label = ttk.Label(
        control_frame,
        text="Downloads: 0",
        font=("Segoe UI", 10)
    )
    count_label.pack(anchor="w", pady=5)

    def on_download():
        if enabled_var.get():
            current = download_count.get()
            download_count.set(current + 1)
            count_label.configure(text=f"Downloads: {download_count.get()}")

    download_btn.configure(command=on_download)

    # State color legend
    legend_frame = ttk.LabelFrame(root, text="State Colors", padding=15)
    legend_frame.pack(pady=10, padx=40, fill="x")

    states = [
        ("Normal", "#28a745", "Default green"),
        ("Hover", "#1e7e34", "Medium green when hovering"),
        ("Pressed", "#155724", "Dark green when clicked"),
        ("Disabled", "#6c757d", "Grey when disabled"),
    ]

    for i, (state, color, description) in enumerate(states):
        frame = ttk.Frame(legend_frame)
        frame.pack(fill="x", pady=2)

        ttk.Label(
            frame,
            text=f"• {state}:",
            font=("Segoe UI", 9, "bold"),
            width=10
        ).pack(side="left")

        ttk.Label(
            frame,
            text=color,
            font=("Segoe UI", 9),
            foreground=color,
            width=10
        ).pack(side="left")

        ttk.Label(
            frame,
            text=description,
            font=("Segoe UI", 9),
            foreground="gray"
        ).pack(side="left", padx=5)

    # Instructions
    instructions = ttk.Label(
        root,
        text="Hover, click, and toggle the checkbox to see all state changes",
        font=("Segoe UI", 9),
        foreground="gray",
        padding=10
    )
    instructions.pack(side="bottom")

    root.mainloop()


if __name__ == "__main__":
    main()