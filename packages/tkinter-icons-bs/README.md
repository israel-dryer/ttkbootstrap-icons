# tkinter-icons-bs

General-purpose interface icons in matched outline and filled cuts — the set most likely to have a plain, recognizable glyph for a toolbar button or a menu entry.

If you are building on ttkbootstrap you do not need this pack: that project has Bootstrap icons built in. This one is for tkinter without it.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-bs.svg)](https://pypi.org/project/tkinter-icons-bs/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Bootstrap Icons** — 2,078 icons, upstream v1.13.1. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[bootstrap]"
```

Installing `tkinter-icons-bs` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import BootstrapIcon

root = tk.Tk()

icon = BootstrapIcon("house", size=24, color="#333", style="outline")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

---

## Styles

Bootstrap Icons ships 2 styles:

- `fill`
- `outline` (default)

Pass one as `style=`, or put it in the name — `BootstrapIcon("house", style="fill")` and `BootstrapIcon("house-fill")` are the same icon.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/bootstrap.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Bootstrap Icons — <https://icons.getbootstrap.com/>
- **Upstream license:** <https://github.com/twbs/icons/blob/main/LICENSE> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
