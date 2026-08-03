# tkinter-icons-mat

An icon provider for the `tkinter-icons` library.  
Material Design Icons (community) offers a large collection of UI glyphs as a single TTF.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-mat.svg)](https://pypi.org/project/tkinter-icons-mat/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install tkinter-icons-mat
```

---

## Quick start

```python
import tkinter as tk
from tkinter_icons_mat import MatIcon

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
tkinter-icons
```

Use **Copy Name** in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](https://raw.githubusercontent.com/israel-dryer/tkinter-icons/main/packages/tkinter-icons-mat/browser.png)

---

## License and Attribution

- **Upstream license:** Material Design Icons — https://materialdesignicons.com/
- **Wrapper license:** MIT © Israel Dryer

