# tkinter-icons-gmi

An icon provider for the `tkinter-icons` library.  
Google Material Icons offer baseline, outlined, round, sharp and twotone variants.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-gmi.svg)](https://pypi.org/project/tkinter-icons-gmi/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install tkinter-icons-gmi
```

---

## Quick start

```python
import tkinter as tk
from tkinter_icons_gmi import GMatIcon

root = tk.Tk()

base = GMatIcon("home", 24, "#555", style="baseline")
outlined = GMatIcon("home", 24, "#555", style="outlined")
rounded = GMatIcon("home", 24, "#555", style="round")
sharp = GMatIcon("home", 24, "#555", style="sharp")

for lbl, icon in [
    ("Baseline", base), ("Outlined", outlined), ("Round", rounded), ("Sharp", sharp)
]:
    tk.Button(root, image=icon.image, text=lbl, compound="left").pack()

root.mainloop()
```

---

## Styles

| Variant     | Description               |
|:------------|:--------------------------|
| `baseline`  | Standard Material baseline|
| `outlined`  | Outline variant           |
| `round`     | Rounded corners           |
| `sharp`     | Sharper corners           |

---

## Icon Browser

Browse available icons with the built-in browser. From your terminal run:

```bash
tkinter-icons
```

Use **Copy Name** in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](https://raw.githubusercontent.com/israel-dryer/tkinter-icons/main/packages/tkinter-icons-gmi/browser.png)

---

## License and Attribution

- **Upstream license:** Google Material Icons — https://fonts.google.com/icons
- **Wrapper license:** MIT © Israel Dryer

