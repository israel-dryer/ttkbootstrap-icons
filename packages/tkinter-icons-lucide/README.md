# tkinter-icons-lucide

An icon provider for the `tkinter-icons` library.  
Lucide Icons are crisp, outline-based glyphs that work well at various sizes.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-lucide.svg)](https://pypi.org/project/tkinter-icons-lucide/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install tkinter-icons-lucide
```

---

## Quick start

```python
import tkinter as tk
from tkinter_icons_lucide import LucideIcon

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
tkinter-icons
```

Use **Copy Name** in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](https://raw.githubusercontent.com/israel-dryer/tkinter-icons/main/packages/tkinter-icons-lucide/browser.png)

---

## License and Attribution

- **Upstream license:** Lucide — https://lucide.dev/
- **Wrapper license:** MIT © Israel Dryer

