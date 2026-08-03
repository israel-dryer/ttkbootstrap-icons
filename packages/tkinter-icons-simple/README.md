# tkinter-icons-simple

An icon provider for the `tkinter-icons` library.  
Simple Icons provides brand logos as a simple, monochrome font.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-simple.svg)](https://pypi.org/project/tkinter-icons-simple/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Simple Icons** — 3,369 icons, upstream v15.18.0. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[simple]"
```

Installing `tkinter-icons-simple` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import SimpleIcon

root = tk.Tk()

icon = SimpleIcon("github", size=24, color="#333")
tk.Button(root, image=icon.image, text="Sign in with GitHub", compound="left").pack()

root.mainloop()
```

---

## Styles

This pack ships a single font with no style variants, so there is no `style` argument.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/simple.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Simple Icons — <https://simpleicons.org/>
- **Upstream license:** <https://github.com/simple-icons/simple-icons/blob/develop/LICENSE.md> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
