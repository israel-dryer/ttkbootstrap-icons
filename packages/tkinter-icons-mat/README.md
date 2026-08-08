# tkinter-icons-mat

The community-maintained Material Design Icons, in outline and filled cuts, and the largest set of the sixteen.

Broad enough that it usually has a glyph for a specific domain concept, not only for generic interface actions.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-mat.svg)](https://pypi.org/project/tkinter-icons-mat/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Material Design Icons** — 14,896 icons, upstream v7.4.47. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[material]"
```

Installing `tkinter-icons-mat` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import MaterialIcon

root = tk.Tk()

icon = MaterialIcon("home", size=24, color="#333", style="fill")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

`MaterialIcon` is also exported as `MatIcon`; both spellings resolve to the same class.

---

## Styles

Material Design Icons ships 2 styles:

- `outline`
- `fill` (default)

Pass one as `style=`, or put it in the name — `MaterialIcon("home", style="outline")` and `MaterialIcon("home-outline")` are the same icon.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/material.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Material Design Icons — <https://pictogrammers.com/library/mdi/>
- **Upstream license:** <https://pictogrammers.com/docs/general/license/> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
