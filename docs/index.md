# ttkbootstrap-icons

Font-based icons for Tkinter and ttkbootstrap, with a built-in Bootstrap Icons set and optional provider packages (Font Awesome, Material, Remix, Fluent, Simple, Weather, Lucide, Eva, Typicons, and more). Includes a lightweight Icon Browser to search and copy names.

---

## Highlights

- Built-in Bootstrap Icons provider
- Install-and-use provider packages (auto-discovered)
- Simple Python API for size, color, and style
- Fast Icon Browser to preview and copy names
- Pure-Python rendering with Pillow

---

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

![Icon Browser](providers/assets/bootstrap/browser.png)

```bash
ttkbootstrap-icons
# or
python -m ttkbootstrap_icons.browser
```

See the Icon Browser page for details.

---

## Providers

Install one or more provider packages to add more icon sets. Common examples:

```bash
pip install ttkbootstrap-icons-fa        # Font Awesome Free
pip install ttkbootstrap-icons-gmi       # Google Material Icons
pip install ttkbootstrap-icons-remix     # Remix Icon
pip install ttkbootstrap-icons-fluent    # Fluent System Icons
pip install ttkbootstrap-icons-simple    # Simple Icons (brand logos)
pip install ttkbootstrap-icons-weather   # Weather Icons
pip install ttkbootstrap-icons-typicons  # Typicons
```

Providers are auto-discovered by entry points; restart the browser after installing new ones.

---

## Next steps

- Getting Started: first icon, browser, providers
- Icon Browser: usage and troubleshooting
- Providers: per-set notes and examples
- License: MIT license and third-party notices
