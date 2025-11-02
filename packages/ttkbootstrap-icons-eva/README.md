# ttkbootstrap-icons-eva

An icon provider for the `ttkbootstrap-icons` library.  
Eva Icons offers clean outline and filled variants for modern UIs.

[![PyPI](https://img.shields.io/pypi/v/ttkbootstrap-icons-eva.svg)](https://pypi.org/project/ttkbootstrap-icons-eva/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install ttkbootstrap-icons-eva
```

---

## Quick start

```python
import tkinter as tk
from ttkbootstrap_icons_eva import EvaIcon

root = tk.Tk()

outline = EvaIcon("activity", size=24, color="#333", style="outline")
filled = EvaIcon("activity", size=24, color="#333", style="fill")

tk.Button(root, image=outline.image, text="Outline", compound="left").pack()
tk.Button(root, image=filled.image, text="Fill", compound="left").pack()

root.mainloop()
```

---

## Styles

| Variant  | Description            |
|:---------|:-----------------------|
| `outline`| Outline stroke variant |
| `fill`   | Filled variant         |

---

## Icon Browser

Browse available icons with the built-in browser. From your terminal run:

```bash
ttkbootstrap-icons
```

Use **Copy Name** in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](https://raw.githubusercontent.com/israel-dryer/ttkbootstrap-icons/main/packages/ttkbootstrap-icons-eva/browser.png)

---

## License and Attribution

- **Upstream license:** MIT (Eva Icons) - https://github.com/akveo/eva-icons
- **Wrapper license:** MIT - Israel Dryer
