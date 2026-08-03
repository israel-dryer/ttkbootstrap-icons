# tkinter-icons-rpga

An icon provider for the `tkinter-icons` library.  
RPG Awesome is a fantasy-themed set of glyphs based on Font Awesome.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-rpga.svg)](https://pypi.org/project/tkinter-icons-rpga/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**RPG Awesome** — 990 icons, upstream v1.0.0. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[rpg-awesome]"
```

Installing `tkinter-icons-rpga` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import RpgAwesomeIcon

root = tk.Tk()

icon = RpgAwesomeIcon("broadsword", size=24, color="#333")
tk.Button(root, image=icon.image, text="Inventory", compound="left").pack()

root.mainloop()
```

`RpgAwesomeIcon` is also exported as `RPGAIcon`; both spellings resolve to the same class.

---

## Styles

This pack ships a single font with no style variants, so there is no `style` argument.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/rpg-awesome.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** RPG Awesome — <https://nagoshiashumari.github.io/Rpg-Awesome/>
- **Upstream license:** <https://github.com/nagoshiashumari/Rpg-Awesome/blob/master/LICENSE.md> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
