"""
State Comparison Visual
Shows all button states side by side for documentation screenshots.
"""
import ttkbootstrap as tb

from ttkbootstrap_icons_fa import FAIcon


def main():
    root = tb.Window(themename="cosmo")
    root.title("State Comparison - Stateful Icons")
    root.geometry("600x400")

    # Header
    header = tb.Label(
        root,
        text="Button State Comparison",
        font=("Segoe UI", 16, "bold"),
        padding=20
    )
    header.pack()

    # Container frame
    container = tb.Frame(root, padding=20)
    container.pack(fill="both", expand=True)

    # Normal state
    tb.Label(container, text="Normal State:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=5)
    icon1 = FAIcon("heart", size=32, style="solid")
    btn1 = tb.Button(container, text="Like", compound="left", bootstyle="outline-primary")
    icon1.map(btn1)
    btn1.grid(row=0, column=1, padx=20, pady=5)

    # Hover state (simulated with label)
    tb.Label(container, text="Hover State:", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w", pady=5)
    tb.Label(container, text="(Move mouse over button to see)", bootstyle="secondary").grid(row=2, column=0, sticky="w")

    # Pressed state (simulated)
    tb.Label(container, text="Pressed State:", font=("Segoe UI", 11, "bold")).grid(row=3, column=0, sticky="w", pady=5)
    tb.Label(container, text="(Click and hold to see)", bootstyle="secondary").grid(row=4, column=0, sticky="w")

    # Disabled state
    tb.Label(container, text="Disabled State:", font=("Segoe UI", 11, "bold")).grid(
        row=5, column=0, sticky="w", pady=5)
    icon2 = FAIcon("heart", size=32, style="solid")
    btn2 = tb.Button(container, text="Like", compound="left", state="disabled", bootstyle="outline-primary")
    icon2.map(btn2)
    btn2.grid(row=5, column=1, padx=20, pady=5)

    # Info label
    info = tb.Label(
        root,
        text="Hover over and click the top button to see state changes",
        font=("Segoe UI", 9),
        bootstyle="secondary",
        padding=10
    )
    info.pack(side="bottom")

    root.mainloop()


if __name__ == "__main__":
    main()
