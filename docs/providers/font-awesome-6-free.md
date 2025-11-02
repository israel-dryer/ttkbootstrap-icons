# ttkbootstrap-icons-fa

An icon provider for the `ttkbootstrap-icons` library.  
Font Awesome Free offers large, well-known icon sets across solid, regular, and brand categories.

[![PyPI](https://img.shields.io/pypi/v/ttkbootstrap-icons-fa.svg)](https://pypi.org/project/ttkbootstrap-icons-fa/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install ttkbootstrap-icons-fa
```

---

## Quick start

```python
import tkinter as tk
from ttkbootstrap_icons_fa import FAIcon

root = tk.Tk()

solid = FAIcon("house", size=24, color="#0d6efd", style="solid")
regular = FAIcon("house", size=24, color="#0d6efd", style="regular")
brand = FAIcon("github", size=24, color="#0d6efd", style="brands")

tk.Button(root, image=solid.image, text="Solid", compound="left").pack()
tk.Button(root, image=regular.image, text="Regular", compound="left").pack()
tk.Button(root, image=brand.image, text="Brand", compound="left").pack()

root.mainloop()
```

---

## Styles

| Variant   | Description                   |
|:----------|:------------------------------|
| `solid`   | Filled style (most common)    |
| `regular` | Outline/line style            |
| `brands`  | Brand and logo glyphs         |

---

## Icon Browser

Browse available icons with the built-in browser. From your terminal run:

```bash
ttkbootstrap-icons
```

Use **Copy Name** in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](assets/font-awesome-6-free/browser.png)

---

## License and Attribution

- **Upstream license:** Font Awesome (varies by asset) â€” https://fontawesome.com/
- **Wrapper license:** MIT Â© Israel Dryer


