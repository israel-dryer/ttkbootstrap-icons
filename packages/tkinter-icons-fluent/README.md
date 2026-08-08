# tkinter-icons-fluent

Microsoft's system icon set, in regular, filled and light weights. The one to reach for when an application should sit visually alongside Windows 11.

If you only ever use the regular weight, `tkinter-icons[fluent-regular]` ships that alone and is a much smaller download.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-fluent.svg)](https://pypi.org/project/tkinter-icons-fluent/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Fluent System Icons** — 12,879 icons, upstream v1.1.261. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[fluent]"
```

Installing `tkinter-icons-fluent` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import FluentIcon

root = tk.Tk()

icon = FluentIcon("search-32", size=24, color="#333", style="regular")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

---

## Styles

Fluent System Icons ships 3 styles:

- `regular` (default)
- `filled`
- `light`

Pass one as `style=`, or put it in the name — `FluentIcon("search-32", style="regular")` and `FluentIcon("search-32-regular")` are the same icon.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/fluent.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Fluent System Icons — <https://github.com/microsoft/fluentui-system-icons>
- **Upstream license:** <https://github.com/microsoft/fluentui-system-icons/blob/main/LICENSE> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
