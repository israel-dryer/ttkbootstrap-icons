# tkinter-icons-remix

An icon provider for the `tkinter-icons` library.  
Remix Icon offers modern, consistent line and filled variants.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-remix.svg)](https://pypi.org/project/tkinter-icons-remix/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install tkinter-icons-remix
```

---

## Quick start

```python
import tkinter as tk
from tkinter_icons_remix import RemixIcon

root = tk.Tk()

icon = RemixIcon("home-3-fill", size=24, color="#fd7e14")
tk.Label(root, image=icon.image).pack()

root.mainloop()
```

---

## Styles

| Variant | Description        |
|:--------|:-------------------|
| `line`  | Line/outline style |
| `fill`  | Filled style       |

---

## Icon Browser

Browse available icons with the built-in browser. From your terminal run:

```bash
tkinter-icons
```

Use **Copy Name** in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](https://raw.githubusercontent.com/israel-dryer/tkinter-icons/main/packages/tkinter-icons-remix/browser.png)

---

## License and Attribution

- **Upstream license:** Remix Icon — https://remixicon.com/
- **Wrapper license:** MIT © Israel Dryer

