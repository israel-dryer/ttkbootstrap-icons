# ttkbootstrap-icons-meteocons

An icon provider for the `ttkbootstrap-icons` library.  
Meteocons is a compact weather-themed icon font.

[![PyPI](https://img.shields.io/pypi/v/ttkbootstrap-icons-meteocons.svg)](https://pypi.org/project/ttkbootstrap-icons-meteocons/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

---

## Install

```bash
pip install ttkbootstrap-icons-meteocons
```

---

## Quick start

```python
import tkinter as tk
from ttkbootstrap_icons_meteocons import MeteoIcon

root = tk.Tk()

icon = MeteoIcon("a", size=24, color="#0077ff")
tk.Button(root, image=icon.image, text="Meteocons", compound="left").pack()

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

![Icon Browser](https://raw.githubusercontent.com/israel-dryer/ttkbootstrap-icons/main/packages/ttkbootstrap-icons-meteocons/browser.png)

---

## License and Attribution

- **Upstream license:** Meteocons — https://demo.alessioatzeni.com/meteocons/
- **Wrapper license:** MIT © Israel Dryer

