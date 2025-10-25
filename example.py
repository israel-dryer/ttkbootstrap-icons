"""
Example application demonstrating ttkbootstrap-icons usage.
This example is also useful for testing PyInstaller builds.
"""

import atexit
import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons import BootstrapIcon, LucideIcon
from ttkbootstrap_icons.icon import Icon


def main():
    # Register cleanup to remove temporary font files on exit
    atexit.register(Icon.cleanup)

    root = tk.Tk()
    root.title("ttkbootstrap-icons Example")

    # Title
    title = tk.Label(root, text="Icon Examples", font=("Arial", 16, "bold"))
    title.pack(pady=10)

    # Bootstrap Icons
    frame1 = ttk.LabelFrame(root, text="Bootstrap Icons", padding=10)
    frame1.pack(fill="x", padx=20, pady=10)

    icons = [
        ("house", "Home"),
        ("gear", "Settings"),
        ("heart", "Favorite"),
        ("search", "Search"),
    ]

    for icon_name, label_text in icons:
        icon = BootstrapIcon(icon_name, size=24, color="#0d6efd")
        btn = tk.Button(
            frame1, image=icon.image, text=label_text, compound="left", width=120
        )
        btn.pack(side="left", padx=5)
        # Keep reference to prevent garbage collection
        btn.icon = icon

    # Lucide Icons
    frame2 = ttk.LabelFrame(root, text="Lucide Icons", padding=10)
    frame2.pack(fill="x", padx=20, pady=10)

    lucide_icons = [
        ("house", "Home"),
        ("settings", "Settings"),
        ("user", "User"),
        ("bell", "Notifications"),
    ]

    for icon_name, label_text in lucide_icons:
        icon = LucideIcon(icon_name, size=24, color="#dc3545")
        btn = tk.Button(
            frame2, image=icon.image, text=label_text, compound="left", width=120
        )
        btn.pack(side="left", padx=5)
        # Keep reference to prevent garbage collection
        btn.icon = icon

    # Info
    info = tk.Label(
        root,
        text="Icons are rendered from fonts and can be any size/color!",
        font=("Arial", 9),
        fg="gray",
    )
    info.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
