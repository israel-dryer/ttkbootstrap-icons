"""
Debug script to see what style.map() actually returns
"""
import ttkbootstrap as tb


def main():
    root = tb.Window(themename="cosmo")

    # Create a primary button
    btn = tb.Button(root, text="Test", bootstyle="primary")
    btn.pack(padx=20, pady=20)

    style = tb.Style()

    # Check what the button's actual style is
    button_style = btn.cget("style") or btn.winfo_class()
    print(f"Button style: {button_style}")
    print()

    # Check foreground map
    fg_map = style.map(button_style, "foreground")
    print(f"Foreground map type: {type(fg_map)}")
    print(f"Foreground map: {fg_map}")
    print()

    # Check foreground lookup for different states
    print("Foreground lookups:")
    for state in ["", "hover", "pressed", "disabled", "active", "!disabled"]:
        if state:
            color = style.lookup(button_style, "foreground", state=(state,))
        else:
            color = style.lookup(button_style, "foreground")
        print(f"  {state or 'normal':15s}: {color}")
    print()

    # Check background map (might be used instead of foreground)
    bg_map = style.map(button_style, "background")
    print(f"Background map: {bg_map}")
    print()

    # Check what configure returns
    config = style.configure(button_style)
    print(f"Style configuration: {config}")

    root.mainloop()


if __name__ == "__main__":
    main()