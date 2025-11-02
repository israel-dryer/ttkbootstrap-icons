# ttkbootstrap-icons-lucide

An icon provider for the `ttkbootstrap-icons` library.  
Lucide Icons are crisp, outline-based glyphs that work well at various sizes.

[![PyPI](https://img.shields.io/pypi/v/ttkbootstrap-icons-lucide.svg)](https://pypi.org/project/ttkbootstrap-icons-lucide/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install ttkbootstrap-icons-lucide
```

---

## Quick start

```python
import tkinter as tk
from ttkbootstrap_icons_lucide import LucideIcon

root = tk.Tk()

icon = LucideIcon("home", size=24, color="#333")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

---

## Styles

This provider uses a single font without separate style variants.

---

## Icon Browser

Browse available icons with the built-in browser. From your terminal run:

```bash
ttkbootstrap-icons
```

Use **Copy Name** in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](assets/lucide/browser.png)

---

## License and Attribution

- **Upstream license:** Lucide â€” https://lucide.dev/
- **Wrapper license:** MIT Â© Israel Dryer


