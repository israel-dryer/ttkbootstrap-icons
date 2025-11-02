"""
Toggle Button with State Icons
Create a toggle that shows different icons based on its checked state.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap_icons_fa import FAIcon


def main():
    root = tb.Window(themename="cosmo")
    root.title("Toggle Button - Stateful Icons")
    root.geometry("500x400")

    # Header
    header = ttk.Label(
        root,
        text="Toggle Button State Icons",
        font=("Segoe UI", 16, "bold"),
        padding=20
    )
    header.pack()

    # Description
    desc = ttk.Label(
        root,
        text="Toggle notifications on/off to see icon changes\nIcon and color change based on checked state",
        font=("Segoe UI", 10),
        justify="center",
        padding=10
    )
    desc.pack()

    # Container
    container = ttk.Frame(root, padding=30)
    container.pack(expand=True)

    # Create toggle button
    toggle_var = tk.BooleanVar(value=True)
    toggle = ttk.Checkbutton(
        container,
        text="Notifications",
        variable=toggle_var,
        style="success.Toolbutton"
    )

    # Create icon that changes based on checked state
    bell_icon = FAIcon("bell", size=32, style="solid")
    bell_icon.map(
        toggle,
        statespec=[
            ("selected", {"name": "bell", "color": "#28a745"}),        # Green bell when on
            ("!selected", {"name": "bell-slash", "color": "#dc3545"}), # Red muted bell when off
            ("hover selected", {"name": "bell", "color": "#1e7e34"}),  # Darker green on hover
            ("hover !selected", {"name": "bell-slash", "color": "#bd2130"}),  # Darker red on hover
        ]
    )

    toggle.pack(pady=20)

    # Status display
    status_frame = ttk.LabelFrame(container, text="Current Status", padding=20)
    status_frame.pack(pady=20, fill="x")

    status_label = ttk.Label(
        status_frame,
        text="",
        font=("Segoe UI", 12, "bold")
    )
    status_label.pack()

    def update_status(*args):
        if toggle_var.get():
            status_label.configure(text="🔔 Notifications ENABLED", foreground="#28a745")
        else:
            status_label.configure(text="🔕 Notifications DISABLED", foreground="#dc3545")

    toggle_var.trace_add("write", update_status)
    update_status()  # Initial update

    # State legend
    legend_frame = ttk.LabelFrame(root, text="Icon States", padding=15)
    legend_frame.pack(pady=10, padx=40, fill="x")

    ttk.Label(
        legend_frame,
        text="• Enabled (checked): Green bell icon",
        font=("Segoe UI", 9),
        foreground="#28a745"
    ).pack(anchor="w", pady=2)

    ttk.Label(
        legend_frame,
        text="• Disabled (unchecked): Red bell-slash icon",
        font=("Segoe UI", 9),
        foreground="#dc3545"
    ).pack(anchor="w", pady=2)

    ttk.Label(
        legend_frame,
        text="• Hover: Darker shade of current state color",
        font=("Segoe UI", 9),
        foreground="gray"
    ).pack(anchor="w", pady=2)

    root.mainloop()


if __name__ == "__main__":
    main()