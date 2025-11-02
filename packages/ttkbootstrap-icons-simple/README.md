# ttkbootstrap-icons-simple

An icon provider for the `ttkbootstrap-icons` library.  
Simple Icons provides brand logos as a simple, monochrome font.

[![PyPI](https://img.shields.io/pypi/v/ttkbootstrap-icons-simple.svg)](https://pypi.org/project/ttkbootstrap-icons-simple/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install ttkbootstrap-icons-simple
```

---

## Quick start

```python
import tkinter as tk
from ttkbootstrap_icons_simple import SimpleIcon

root = tk.Tk()

icon = SimpleIcon("python", size=24, color="#333333")
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

- **Upstream license:** Simple Icons — https://simpleicons.org/
- **Wrapper license:** MIT © Israel Dryer
