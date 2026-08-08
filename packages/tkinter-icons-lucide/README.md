# tkinter-icons-lucide

Uniformly stroked hairline outlines, and the lightest-looking set of the sixteen.

A good match for dense interfaces, where heavier glyphs start to dominate the layout.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-lucide.svg)](https://pypi.org/project/tkinter-icons-lucide/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Lucide Icons** — 1,601 icons, upstream v0.511.0. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[lucide]"
```

Installing `tkinter-icons-lucide` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import LucideIcon

root = tk.Tk()

icon = LucideIcon("house", size=24, color="#333")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

---

## Styles

This pack ships a single font with no style variants, so there is no `style` argument.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/lucide.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Lucide Icons — <http://lucide.dev/icons/>
- **Upstream license:** <https://lucide.dev/license> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
