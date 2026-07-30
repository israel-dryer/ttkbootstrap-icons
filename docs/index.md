# tkinter-icons

Font-based icons for Tkinter and ttkbootstrap, with installable provider packages (Bootstrap Icons, Font Awesome, Material, Remix, Fluent, Simple, Weather, Lucide, Eva, Typicons, and more). Includes a lightweight Icon Browser to search and copy names.

---

## Highlights

- Installable provider packages (auto-discovered via entry points)
- Wide selection: Bootstrap, Font Awesome, Material, Fluent, and more
- Simple Python API for size, color, and style
- Fast Icon Browser to preview and copy names
- Pure-Python rendering with Pillow

---

## Install

Install the base package and at least one icon provider:

```bash
pip install tkinter-icons tkinter-icons-bs
```

---

## Quick start

```python
import tkinter as tk
from tkinter_icons_bs import BootstrapIcon

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
tkinter-icons
# or
python -m tkinter_icons.browser
```

See the Icon Browser page for details.

---

## Providers

Install one or more provider packages to add icon sets. Common examples:

```bash
pip install tkinter-icons-bs        # Bootstrap Icons
pip install tkinter-icons-fa        # Font Awesome Free
pip install tkinter-icons-gmi       # Google Material Icons
pip install tkinter-icons-remix     # Remix Icon
pip install tkinter-icons-fluent    # Fluent System Icons
pip install tkinter-icons-simple    # Simple Icons (brand logos)
pip install tkinter-icons-weather   # Weather Icons
pip install tkinter-icons-typicons  # Typicons
```

Providers are auto-discovered by entry points; restart the browser after installing new ones.

---

## Next steps

- Getting Started: first icon, browser, providers
- Icon Browser: usage and troubleshooting
- Providers: per-set notes and examples
- License: MIT license and third-party notices
