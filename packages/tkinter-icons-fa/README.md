# tkinter-icons-fa

A broad interface set alongside a large collection of brand marks, in solid, regular and brands cuts.

The brands cut is the reason to reach for this one: it is the pack that lets a third-party logo sit beside ordinary interface glyphs without installing a second set.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-fa.svg)](https://pypi.org/project/tkinter-icons-fa/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Font Awesome 6 (Free)** — 2,141 icons, upstream v6.7.2. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[fontawesome]"
```

Installing `tkinter-icons-fa` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import FontAwesomeIcon

root = tk.Tk()

icon = FontAwesomeIcon("user", size=24, color="#333", style="solid")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

`FontAwesomeIcon` is also exported as `FAIcon`; both spellings resolve to the same class.

---

## Styles

Font Awesome 6 (Free) ships 3 styles:

- `solid` (default)
- `regular`
- `brands`

Pass one as `style=`, or put it in the name — `FontAwesomeIcon("user", style="solid")` and `FontAwesomeIcon("user-solid")` are the same icon.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/fontawesome.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Font Awesome 6 (Free) — <https://fontawesome.com/v6/icons>
- **Upstream license:** <https://fontawesome.com/license> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
