# ttkbootstrap-icons

[![PyPI](https://img.shields.io/pypi/v/ttkbootstrap-icons.svg)](https://pypi.org/project/ttkbootstrap-icons/)
[![Python Versions](https://img.shields.io/pypi/pyversions/ttkbootstrap-icons.svg)](https://pypi.org/project/ttkbootstrap-icons/)
[![Downloads](https://static.pepy.tech/badge/ttkbootstrap-icons)](https://pepy.tech/project/ttkbootstrap-icons)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../../LICENSE)

Font-based icons for Tkinter and ttkbootstrap, with a built-in Bootstrap Icons set and optional provider packages (Font
Awesome, Material, Remix, Fluent, Simple, Weather, Lucide, Eva, Typicons, and more). Includes a lightweight Icon Browser
to search and copy names.

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

https://israel-dryer.github.io/ttkbootstrap-icons/

## Install

```bash
pip install ttkbootstrap-icons
```

---

## Quick start

```python
import tkinter as tk
from ttkbootstrap_icons import BootstrapIcon

root = tk.Tk()
icon = BootstrapIcon("house", size=24, color="#0d6efd", style="fill")
tk.Label(root, image=icon.image, text=" Home", compound="left").pack(padx=10, pady=10)
root.mainloop()
```

---

## Icon Browser

Search and preview icons across all installed providers, then copy names for use in code.

```bash
ttkbootstrap-icons
# or
python -m ttkbootstrap_icons.browser
```

---

## Links

- Documentation: https://israel-dryer.github.io/ttkbootstrap-icons/
- Repository: https://github.com/israel-dryer/ttkbootstrap-icons

