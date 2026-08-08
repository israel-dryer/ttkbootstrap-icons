# tkinter-icons-ion

Ionicons v2, the interface set from the Ionic framework.

One style and a small download, with glyph shapes most people will already find familiar.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-ion.svg)](https://pypi.org/project/tkinter-icons-ion/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Ion Icons** — 1,414 icons, upstream v2.0.1. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[ionicons]"
```

Installing `tkinter-icons-ion` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import IonIcon

root = tk.Tk()

icon = IonIcon("home", size=24, color="#333")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

---

## Styles

This pack ships a single font with no style variants, so there is no `style` argument.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/ionicons.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Ion Icons — <https://github.com/ionic-team/ionicons>
- **Upstream license:** <https://github.com/ionic-team/ionicons/blob/main/LICENSE> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
