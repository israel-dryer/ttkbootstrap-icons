# tkinter-icons-meteocons

A compact weather set — sun, cloud, precipitation and wind states — drawn by [Alessio Atzeni](https://www.alessioatzeni.com/meteocons/).

For a much larger weather vocabulary, including moon phases and Beaufort codes, install `tkinter-icons[weather]` instead.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-meteocons.svg)](https://pypi.org/project/tkinter-icons-meteocons/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Meteocons** — 94 icons, upstream v1.0. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[meteocons]"
```

Installing `tkinter-icons-meteocons` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import MeteoconsIcon

root = tk.Tk()

icon = MeteoconsIcon("sun", size=24, color="#333")
tk.Button(root, image=icon.image, text="Forecast", compound="left").pack()

root.mainloop()
```

`MeteoconsIcon` is also exported as `MeteoIcon`; both spellings resolve to the same class.

---

## Styles

This pack ships a single font with no style variants, so there is no `style` argument.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/meteocons.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Meteocons — <https://www.alessioatzeni.com/meteocons/>
- **Upstream license:** <https://www.alessioatzeni.com/meteocons/> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
