# Getting Started

This guide helps you install ttkbootstrap-icons, render your first icon in Tkinter, and browse additional icon sets via provider packages.

---

## Requirements

- Python 3.10+
- Pillow (installed automatically by the packages below)
- Tkinter (bundled with most Python distributions)

---

## Install the base package

The base package includes the built-in Bootstrap Icons provider and the Icon Browser app.

```bash
pip install ttkbootstrap-icons
```

---

## Your first icon (Bootstrap)

Render a Bootstrap icon using the built-in provider:

```python
import tkinter as tk
from ttkbootstrap_icons import BootstrapIcon

root = tk.Tk()
root.title("Hello Icons")

icon = BootstrapIcon("house", size=32, color="#0d6efd", style="fill")
label = tk.Label(root, image=icon.image, text=" Home", compound="left")
label.pack(padx=10, pady=10)

root.mainloop()
```

Notes
- The `name` can be a base name (e.g., `house`) or a fully-qualified name with a suffix (e.g., `house-fill`).
- The `style` parameter (when supported) can select a variant (e.g., `fill`, `outline`).
- `size` is in pixels; `color` accepts any Tk-compatible color string (e.g., hex).

---

## Browse available icons

Launch the graphical browser to search and preview icons (built-in + any installed providers):

```bash
# CLI
ttkbootstrap-icons

# or via Python
python -m ttkbootstrap_icons.browser
```

See: Icon Browser for details.

---

## Add more icon sets (providers)

Install one or more provider packages. The browser and API will auto-discover them.

```bash
# Examples (install any you need)
pip install ttkbootstrap-icons-fa         # Font Awesome Free
pip install ttkbootstrap-icons-gmi        # Google Material Icons
pip install ttkbootstrap-icons-remix      # Remix Icon
pip install ttkbootstrap-icons-fluent     # Fluent System Icons
pip install ttkbootstrap-icons-simple     # Simple Icons (brand logos)
pip install ttkbootstrap-icons-weather    # Weather Icons
pip install ttkbootstrap-icons-typicons   # Typicons
```

Using a provider in code:

```python
import tkinter as tk
from ttkbootstrap_icons_fa import FAIcon

root = tk.Tk()
solid = FAIcon("house", size=24, color="#0d6efd", style="solid")
tk.Button(root, image=solid.image, text="Solid", compound="left").pack()
root.mainloop()
```

Style tips
- Providers may support styles (e.g., `fill/outline`, `solid/regular/brands`).
- If a style suffix is already part of the name (e.g., `...-fill`), it takes precedence over the `style` parameter.

---

## Using stateful icons

Icons can automatically change their appearance based on widget states like hover, pressed, disabled, or selected. This creates dynamic, interactive interfaces with minimal code.

### Simple toggle example

Here's how to create a toggle button that switches between two different icons:

```python
import ttkbootstrap as tb
from ttkbootstrap_icons import BootstrapIcon

app = tb.Window("Toggle Icon")

# Create an icon that starts as muted
sound = BootstrapIcon("mic-mute-fill", size=64)

# Create a toggle button
toggle = tb.Checkbutton(app, compound="image", bootstyle="toolbutton")
toggle.pack(padx=20, pady=20)

# Map the icon to change when selected
sound.map(toggle, statespec=[("selected", {"name": "mic-fill"})])

app.mainloop()
```

When you click the toggle, the icon automatically switches from `mic-mute-fill` to `mic-fill`. The stateful icon system handles all the state detection and rendering for you.

**Other possibilities:**
- Change icon colors on hover for visual feedback
- Display dimmed icons when widgets are disabled
- Highlight active navigation items with distinct colors
- Create press animations by changing colors when clicked

See [Stateful Icons](stateful-icons.md) for complete documentation, including automatic color mapping, custom state specifications, and advanced examples.

---

## Troubleshooting

Provider not showing in the browser
- Confirm the provider is installed in the same Python environment as the browser:

```bash
python -c "from importlib.metadata import entry_points; print([ (e.name, e.value) for e in entry_points(group='ttkbootstrap_icons.providers') ])"
```

- Restart the browser after installing new providers.

Import or rendering errors
- Update to the latest versions:

```bash
pip install -U ttkbootstrap-icons
```

- Ensure the provider package is up-to-date and that its fonts/glyphmap files are present.

---

## Next steps

- Explore Providers in the sidebar for per-set details.
- Use the Icon Browser to search and copy icon names styled to your needs.
