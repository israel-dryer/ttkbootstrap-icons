# tkinter-icons-weather

An icon provider for the `tkinter-icons` library.  
Weather Icons is a classic set of weather-related glyphs.

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons-weather.svg)](https://pypi.org/project/tkinter-icons-weather/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license-and-attribution)

**Weather Icons** — 1,182 icons, upstream v2.0.10. One of sixteen icon packs for [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).

---

## Install

This pack is an extra of `tkinter-icons`, so you install and import one name:

```bash
pip install "tkinter-icons[weather]"
```

Installing `tkinter-icons-weather` directly also works and pulls in the base package, but the extra is the supported form — it is what the error messages, the documentation, and the other fifteen packs all use.

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import WeatherIcon

root = tk.Tk()

icon = WeatherIcon("day-sunny", size=24, color="#333")
tk.Button(root, image=icon.image, text="Forecast", compound="left").pack()

root.mainloop()
```

---

## Styles

This pack ships a single font with no style variants, so there is no `style` argument.

---

## Browse the icons

Every glyph in this pack, rendered by the library itself:
<https://tkinter-icons.readthedocs.io/en/latest/packs/weather.html>

Or run the browser that ships with the base package:

```bash
tkinter-icons
```

Use **Copy Name** there to copy an icon name straight into your code.

---

## License and attribution

- **Upstream:** Weather Icons — <https://erikflowers.github.io/weather-icons/>
- **Upstream license:** <https://github.com/erikflowers/weather-icons#licensing> — see `LICENSES/` in this package
- **Wrapper license:** MIT © Israel Dryer
