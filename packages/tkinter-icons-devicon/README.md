# tkinter-icons-devicon

Logos for programming languages, frameworks and developer tools, in plain and original cuts.

Many names also come as a wordmark variant, which sets the product's name beside the mark — useful on a splash screen or an about box, less so on a toolbar.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-devicon.svg)](https://pypi.org/project/tkinter-icons-devicon/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Devicon** — 1,229 icons, upstream v2.17.0. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[devicon]"
```

Installing `tkinter-icons-devicon` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import DeviconIcon

root = tk.Tk()

icon = DeviconIcon("python", size=24, color="#333", style="plain")
tk.Button(root, image=icon.image, text="Python", compound="left").pack()

root.mainloop()
```

`DeviconIcon` is also exported as `DevIcon`; both spellings resolve to the same class.

---

## Styles

Devicon ships 4 styles:

- `plain` (default)
- `plain-wordmark`
- `original`
- `original-wordmark`

Pass one as `style=`, or put it in the name — `DeviconIcon("python", style="plain")` and `DeviconIcon("python-plain")` are the same icon.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/devicon.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Devicon — <https://devicon.dev/>
- **Upstream license:** <https://github.com/devicons/devicon/blob/master/LICENSE> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
