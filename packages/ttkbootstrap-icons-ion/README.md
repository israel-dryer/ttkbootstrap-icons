# ttkbootstrap-icons-ion

An icon provider for the `ttkbootstrap-icons` library.  
Ionicons v2 provides a familiar set of UI glyphs as a single TTF font.

[![PyPI](https://img.shields.io/pypi/v/ttkbootstrap-icons-ion.svg)](https://pypi.org/project/ttkbootstrap-icons-ion/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install ttkbootstrap-icons-ion
```

---

## Quick start

```python
import tkinter as tk
from ttkbootstrap_icons_ion import IonIcon

root = tk.Tk()

icon = IonIcon("home", size=24, color="#198754")
tk.Button(root, image=icon.image).pack()

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

![Icon Browser](https://raw.githubusercontent.com/israel-dryer/ttkbootstrap-icons/main/packages/ttkbootstrap-icons-ion/browser.png)

---

## License and Attribution

- **Upstream license:** Ionicons — https://ionic.io/ionicons
- **Wrapper license:** MIT © Israel Dryer

