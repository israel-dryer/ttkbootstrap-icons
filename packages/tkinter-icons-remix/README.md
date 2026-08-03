# tkinter-icons-remix

An icon provider for the `tkinter-icons` library.  
Remix Icon offers modern, consistent line and filled variants.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-remix.svg)](https://pypi.org/project/tkinter-icons-remix/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Remix Icon** — 2,356 icons, upstream v4.7.0. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[remix]"
```

Installing `tkinter-icons-remix` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import RemixIcon

root = tk.Tk()

icon = RemixIcon("home", size=24, color="#333", style="fill")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

---

## Styles

Remix Icon ships 2 styles:

- `line`
- `fill` (default)

Pass one as `style=`, or put it in the name — `RemixIcon("home", style="line")` and `RemixIcon("home-line")` are the same icon.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/remix.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Remix Icon — <https://remixicon.com/>
- **Upstream license:** <https://github.com/Remix-Design/RemixIcon/blob/master/License> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
