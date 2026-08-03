# tkinter-icons-eva

An icon provider for the `tkinter-icons` library.  
Eva Icons offers clean outline and filled variants for modern UIs.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-eva.svg)](https://pypi.org/project/tkinter-icons-eva/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Eva Icons** — 980 icons, upstream v1.1.3. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[eva]"
```

Installing `tkinter-icons-eva` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import EvaIcon

root = tk.Tk()

icon = EvaIcon("home", size=24, color="#333", style="fill")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

---

## Styles

Eva Icons ships 2 styles:

- `outline`
- `fill` (default)

Pass one as `style=`, or put it in the name — `EvaIcon("home", style="outline")` and `EvaIcon("home-outline")` are the same icon.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/eva.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Eva Icons — <https://akveo.github.io/eva-icons/#/>
- **Upstream license:** <https://github.com/akveo/eva-icons/blob/master/LICENSE.txt> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
