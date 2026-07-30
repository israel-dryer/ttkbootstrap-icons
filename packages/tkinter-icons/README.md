# tkinter-icons

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons.svg)](https://pypi.org/project/tkinter-icons/)
[![Python Versions](https://img.shields.io/pypi/pyversions/tkinter-icons.svg)](https://pypi.org/project/tkinter-icons/)
[![Downloads](https://static.pepy.tech/badge/tkinter-icons)](https://pepy.tech/project/tkinter-icons)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../../LICENSE)

Base package for font-based icons in Tkinter and ttkbootstrap. Provides the provider framework and Icon Browser. Install icon provider packages separately (Bootstrap Icons, Font Awesome, Material, Remix, Fluent, Simple, Weather, Lucide, Eva, Typicons, and more).

---

## Highlights

- Built-in Bootstrap Icons provider
- Install-and-use provider packages (auto-discovered)
- Simple Python API for size, color, and style
- Fast Icon Browser to preview and copy names
- Pure-Python rendering with Pillow

---

## Documentation

Full documentation, provider list, API reference, and usage guides:

https://israel-dryer.github.io/tkinter-icons/

## Install

```bash
pip install tkinter-icons
```

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import BootstrapIcon

root = tk.Tk()
icon = BootstrapIcon("house", size=24, color="#0d6efd", style="fill")
tk.Label(root, image=icon.image, text=" Home", compound="left").pack(padx=10, pady=10)
root.mainloop()
```

---

## Stateful Icons (v3.1.0+)

Icons can automatically change appearance based on widget states (hover, pressed, disabled, selected):

```python
import ttkbootstrap as tb
from tkinter_icons import BootstrapIcon

app = tb.Window()
icon = BootstrapIcon("mic-mute-fill", size=64)
toggle = tb.Checkbutton(app, compound="image", bootstyle="toolbutton")
toggle.pack(padx=20, pady=20)

# Icon automatically switches to mic-fill when selected
icon.map(toggle, statespec=[("selected", {"name": "mic-fill"})])

app.mainloop()
```

See the [Stateful Icons documentation](https://israel-dryer.github.io/tkinter-icons/stateful-icons/) for automatic color mapping, custom state specifications, and advanced examples.

---

## Icon Browser

Search and preview icons across all installed providers, then copy names for use in code.

```bash
tkinter-icons
# or
python -m tkinter_icons.browser
```

---

## Links

- Documentation: https://israel-dryer.github.io/tkinter-icons/
- Repository: https://github.com/israel-dryer/tkinter-icons

