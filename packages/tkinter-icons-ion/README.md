# tkinter-icons-ion

An icon provider for the `tkinter-icons` library.  
Ionicons v2 provides a familiar set of UI glyphs as a single TTF font.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-ion.svg)](https://pypi.org/project/tkinter-icons-ion/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install tkinter-icons-ion
```

---

## Quick start

```python
import tkinter as tk
from tkinter_icons_ion import IonIcon

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
tkinter-icons
```

Use **Copy Name** in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](https://raw.githubusercontent.com/israel-dryer/tkinter-icons/main/packages/tkinter-icons-ion/browser.png)

---

## License and Attribution

- **Upstream license:** Ionicons — https://ionic.io/ionicons
- **Wrapper license:** MIT © Israel Dryer

