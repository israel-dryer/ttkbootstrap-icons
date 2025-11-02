# ttkbootstrap-icons-gmi

An icon provider for the `ttkbootstrap-icons` library.  
Google Material Icons offer baseline, outlined, round, sharp and twotone variants.

[![PyPI](https://img.shields.io/pypi/v/ttkbootstrap-icons-gmi.svg)](https://pypi.org/project/ttkbootstrap-icons-gmi/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install ttkbootstrap-icons-gmi
```

---

## Quick start

```python
import tkinter as tk
from ttkbootstrap_icons_gmi import GMatIcon

root = tk.Tk()

base = GMatIcon("home", 24, "#555", style="baseline")
outlined = GMatIcon("home", 24, "#555", style="outlined")
rounded = GMatIcon("home", 24, "#555", style="round")
sharp = GMatIcon("home", 24, "#555", style="sharp")
twotone = GMatIcon("home", 24, "#555", style="twotone")

for lbl, icon in [
    ("Baseline", base), ("Outlined", outlined), ("Round", rounded), ("Sharp", sharp), ("TwoTone", twotone)
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
| `twotone`   | Two-tone variant          |

---

## Icon Browser

Browse available icons with the built-in browser. From your terminal run:

```bash
ttkbootstrap-icons
```

Use **Copy Name** in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](assets/google-material-icons/browser.png)

---

## License and Attribution

- **Upstream license:** Google Material Icons â€” https://fonts.google.com/icons
- **Wrapper license:** MIT © Israel Dryer



