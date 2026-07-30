# tkinter-icons-rpga

An icon provider for the `tkinter-icons` library.  
RPG Awesome is a fantasy-themed set of glyphs based on Font Awesome.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-rpga.svg)](https://pypi.org/project/tkinter-icons-rpga/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install tkinter-icons-rpga
```

---

## Quick start

```python
import tkinter as tk
from tkinter_icons_rpga import RPGAIcon

root = tk.Tk()

icon = RPGAIcon("bat-sword", size=24, color="#6f42c1")
tk.Button(root, image=icon.image, text="Sword", compound="left").pack()

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

![Icon Browser](https://raw.githubusercontent.com/israel-dryer/tkinter-icons/main/packages/tkinter-icons-rpga/browser.png)

---

## License and Attribution

- **Upstream license:** RPG Awesome — https://nagoshiashumari.github.io/Rpg-Awesome/
- **Wrapper license:** MIT © Israel Dryer

