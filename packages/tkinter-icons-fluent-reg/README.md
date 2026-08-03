# tkinter-icons-fluent-reg

Fluent System Icons (Regular style only) provider for tkinter-icons.

This is a lightweight pack that includes only the Regular style from Microsoft's Fluent System Icons. If you need multiple styles (Regular, Filled, Light), install `"tkinter-icons[fluent]"` instead.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-fluent-reg.svg)](https://pypi.org/project/tkinter-icons-fluent-reg/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Fluent System Icons (Regular)** — 6,336 icons, upstream v1.1.261. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[fluent-regular]"
```

Installing `tkinter-icons-fluent-reg` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import FluentRegularIcon

root = tk.Tk()

icon = FluentRegularIcon("home-24", size=24, color="#333")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

---

## Styles

This pack ships a single font with no style variants, so there is no `style` argument.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/fluent-regular.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Fluent System Icons (Regular) — <https://github.com/microsoft/fluentui-system-icons>
- **Upstream license:** <https://github.com/microsoft/fluentui-system-icons/blob/main/LICENSE> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
