# ttkbootstrap-icons-mat

An icon provider for the `ttkbootstrap-icons` library.  
Material Design Icons (community) offers a large collection of UI glyphs as a single TTF.

[![PyPI](https://img.shields.io/pypi/v/ttkbootstrap-icons-mat.svg)](https://pypi.org/project/ttkbootstrap-icons-mat/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install ttkbootstrap-icons-mat
```

---

## Quick start

```python
import tkinter as tk
from ttkbootstrap_icons_mat import MatIcon

root = tk.Tk()

icon = MatIcon("home", size=24, color="#dc3545")
tk.Label(root, image=icon.image).pack()

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

![Icon Browser](browser.png)

---

## License and Attribution

- **Upstream license:** Material Design Icons — https://materialdesignicons.com/
- **Wrapper license:** MIT © Israel Dryer

