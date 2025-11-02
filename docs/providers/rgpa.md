# ttkbootstrap-icons-rpga

An icon provider for the `ttkbootstrap-icons` library.  
RPG Awesome is a fantasy-themed set of glyphs based on Font Awesome.

[![PyPI](https://img.shields.io/pypi/v/ttkbootstrap-icons-rpga.svg)](https://pypi.org/project/ttkbootstrap-icons-rpga/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install ttkbootstrap-icons-rpga
```

---

## Quick start

```python
import tkinter as tk
from ttkbootstrap_icons_rpga import RPGAIcon

root = tk.Tk()

icon = RPGAIcon("sword", size=24, color="#6f42c1")
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
ttkbootstrap-icons
```

Use **Copy Name** in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](assets/rgpa/browser.png)

---

## License and Attribution

- **Upstream license:** RPG Awesome â€” https://nagoshiashumari.github.io/Rpg-Awesome/
- **Wrapper license:** MIT © Israel Dryer



