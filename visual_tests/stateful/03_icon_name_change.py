"""
Change Icon Name Per State
Display entirely different icons for different states.
"""


import ttkbootstrap as tb
from ttkbootstrap_icons_fa import FAIcon


def main():
    root = tb.Window(themename="cosmo")
    root.title("Icon Name Change - Stateful Icons")
    root.geometry("500x350")

    # Header
    header = tb.Label(
        root,
        text="Icon Name Change on State",
        font=("Segoe UI", 16, "bold"),
        padding=20
    )
    header.pack()

    # Description
    desc = tb.Label(
        root,
        text="Bookmark switches from regular to solid on hover\nand changes color when pressed",
        font=("Segoe UI", 10),
        justify="center",
        padding=10
    )
    desc.pack()

    # Container
    container = tb.Frame(root, padding=30)
    container.pack(expand=True)

    # Create bookmark icon (regular style)
    icon = FAIcon("bookmark", size=48, style="regular")

    # Create button
    button = tb.Button(container, text="Save for Later", compound="left", bootstyle="info")

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
    info_frame = tb.LabelFrame(root, text="State Behavior", padding=15)
    info_frame.pack(pady=10, padx=40, fill="x")

    tb.Label(
        info_frame,
        text="• Normal: Regular outline bookmark (default color)",
        font=("Segoe UI", 9),
        justify="left"
    ).pack(anchor="w", pady=2)

    tb.Label(
        info_frame,
        text="• Hover: Filled bookmark with blue color (#007bff)",
        font=("Segoe UI", 9),
        justify="left"
    ).pack(anchor="w", pady=2)

    tb.Label(
        info_frame,
        text="• Pressed: Filled bookmark with darker blue (#0056b3)",
        font=("Segoe UI", 9),
        justify="left"
    ).pack(anchor="w", pady=2)

    # Additional example button
    tb.Label(root, text="Compare with normal button:", font=("Segoe UI", 9), bootstyle="secondary").pack(pady=(20, 5))
    normal_btn = tb.Button(root, text="No State Mapping", bootstyle="info")
    normal_btn.pack()

    root.mainloop()


if __name__ == "__main__":
    main()