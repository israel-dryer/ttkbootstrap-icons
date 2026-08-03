# tkinter-icons-gmi

An icon provider for the `tkinter-icons` library.  
Google Material Icons offer baseline, outlined, round, sharp and twotone variants.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-gmi.svg)](https://pypi.org/project/tkinter-icons-gmi/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Google Material Icons** — 8,936 icons, upstream v0.14.15. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[google-material]"
```

Installing `tkinter-icons-gmi` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import GoogleMaterialIcon

root = tk.Tk()

icon = GoogleMaterialIcon("home", size=24, color="#333", style="baseline")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

`GoogleMaterialIcon` is also exported as `GMatIcon`; both spellings resolve to the same class.

---

## Styles

Google Material Icons ships 4 styles:

- `baseline` (default)
- `outlined`
- `round`
- `sharp`

Pass one as `style=`, or put it in the name — `GoogleMaterialIcon("home", style="baseline")` and `GoogleMaterialIcon("home-baseline")` are the same icon.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/google-material.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Google Material Icons — <https://github.com/marella/material-design-icons>
- **Upstream license:** <https://github.com/marella/material-design-icons/blob/main/LICENSE> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
