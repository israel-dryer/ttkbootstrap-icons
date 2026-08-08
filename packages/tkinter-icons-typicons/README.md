# tkinter-icons-typicons

A compact pictographic set in outline and filled cuts, with denser, heavier shapes than the hairline sets here.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-typicons.svg)](https://pypi.org/project/tkinter-icons-typicons/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Typicons** — 672 icons, upstream v2.1.2. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[typicons]"
```

Installing `tkinter-icons-typicons` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import TypiconsIcon

root = tk.Tk()

icon = TypiconsIcon("home", size=24, color="#333", style="fill")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

---

## Styles

Typicons ships 2 styles:

- `outline`
- `fill` (default)

Pass one as `style=`, or put it in the name — `TypiconsIcon("home", style="outline")` and `TypiconsIcon("home-outline")` are the same icon.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/typicons.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Typicons — <https://www.s-ings.com/typicons/>
- **Upstream license:** <https://github.com/stephenhutchings/typicons.font/blob/master/LICENCE.md> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
