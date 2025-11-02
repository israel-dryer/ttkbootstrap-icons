"""
Navigation Buttons with Active State
Create navigation items that highlight when selected.
"""
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap_icons_fa import FAIcon


def main():
    root = tb.Window(themename="cosmo")
    root.title("Navigation Buttons - Stateful Icons")
    root.geometry("600x400")

    # Header
    header = tb.Label(
        root,
        text="Navigation with Active States",
        font=("Segoe UI", 16, "bold"),
        padding=20
    )
    header.pack()

    # Description
    desc = tb.Label(
        root,
        text="Click navigation items to see active state changes",
        font=("Segoe UI", 10),
        padding=10
    )
    desc.pack()

    # Navigation frame
    nav_frame = tb.Frame(root, padding=20)
    nav_frame.pack(fill="x")

    # Track active button
    active_button = tk.StringVar(value="home")

    def set_active(button_name, *buttons_to_update):
        """Set the active button and update all button states"""
        active_button.set(button_name)
        for btn_name, btn_widget in buttons_to_update:
            if btn_name == button_name:
                btn_widget.state(['selected'])
            else:
                btn_widget.state(['!selected'])

    # Home button with active state
    home_icon = FAIcon("house", size=20, style="solid")
    home_btn = tb.Button(nav_frame, text="Home", compound="left")
    home_btn.state(['selected'])  # Start as selected
    home_icon.map(
        home_btn,
        statespec=[
            ("selected", "#007bff"),     # Blue when selected/active
            ("hover !selected", "#0056b3"),  # Darker blue on hover when not selected
            ("!selected", "#6c757d"),    # Grey when not selected
        ]
    )
    home_btn.pack(side="left", padx=5)

    # Profile button
    profile_icon = FAIcon("user", size=20, style="solid")
    profile_btn = tb.Button(nav_frame, text="Profile", compound="left")
    profile_icon.map(
        profile_btn,
        statespec=[
            ("selected", "#007bff"),
            ("hover !selected", "#0056b3"),
            ("!selected", "#6c757d"),
        ]
    )
    profile_btn.pack(side="left", padx=5)

    # Settings button
    settings_icon = FAIcon("gear", size=20, style="solid")
    settings_btn = tb.Button(nav_frame, text="Settings", compound="left")
    settings_icon.map(
        settings_btn,
        statespec=[
            ("selected", "#007bff"),
            ("hover !selected", "#0056b3"),
            ("!selected", "#6c757d"),
        ]
    )
    settings_btn.pack(side="left", padx=5)

    # Messages button
    messages_icon = FAIcon("envelope", size=20, style="solid")
    messages_btn = tb.Button(nav_frame, text="Messages", compound="left")
    messages_icon.map(
        messages_btn,
        statespec=[
            ("selected", "#007bff"),
            ("hover !selected", "#0056b3"),
            ("!selected", "#6c757d"),
        ]
    )
    messages_btn.pack(side="left", padx=5)

    # List of all buttons for state management
    all_buttons = [
        ("home", home_btn),
        ("profile", profile_btn),
        ("settings", settings_btn),
        ("messages", messages_btn),
    ]

    # Configure button commands
    home_btn.configure(command=lambda: set_active("home", *all_buttons))
    profile_btn.configure(command=lambda: set_active("profile", *all_buttons))
    settings_btn.configure(command=lambda: set_active("settings", *all_buttons))
    messages_btn.configure(command=lambda: set_active("messages", *all_buttons))

    # Content area showing active page
    content_frame = tb.Frame(root, padding=20)
    content_frame.pack(fill="both", expand=True)

    active_label = tb.Label(
        content_frame,
        text="",
        font=("Segoe UI", 24),
        justify="center"
    )
    active_label.pack(expand=True)

    def update_content(*args):
        page = active_button.get().title()
        active_label.configure(text=f"{page} Page Content")

    active_button.trace_add("write", update_content)
    update_content()  # Initial update

    # Legend
    legend_frame = tb.LabelFrame(root, text="Icon States", padding=10)
    legend_frame.pack(pady=10, padx=40, fill="x", side="bottom")

    tb.Label(legend_frame, text="Blue = Active/Selected  |  Grey = Inactive  |  Dark Blue = Hover",
              font=("Segoe UI", 9), bootstyle="secondary").pack()

    root.mainloop()


if __name__ == "__main__":
    main()