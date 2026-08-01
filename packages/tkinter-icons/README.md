# tkinter-icons

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons.svg)](https://pypi.org/project/tkinter-icons/)
[![Python Versions](https://img.shields.io/pypi/pyversions/tkinter-icons.svg)](https://pypi.org/project/tkinter-icons/)
[![Downloads](https://static.pepy.tech/badge/tkinter-icons)](https://pepy.tech/project/tkinter-icons)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../../LICENSE)

Font-based icons for Tkinter — sixteen icon sets, one import root, no image files to manage.

## Install

Icons come from packs, installed as extras. Pick one:

```bash
pip install "tkinter-icons[material]"
```

```python
import tkinter as tk
from tkinter import ttk

from tkinter_icons import MaterialIcon

root = tk.Tk()

home = MaterialIcon("home", size=24, color="#0d6efd")
ttk.Button(root, text="Home", image=home.image, compound="left").pack(padx=20, pady=20)

root.mainloop()
```

The quotes matter — most shells treat unquoted brackets as a glob. Name two packs together as `"tkinter-icons[material,simple]"`.

> **This package on its own draws nothing.** It is the renderer; the glyphs live in the packs. A bare `pip install tkinter-icons` gets you a working renderer with no icons, and asking for an icon class then raises with the exact command you wanted.

## The sixteen packs

`bootstrap` · `devicon` · `eva` · `fluent` · `fluent-regular` · `fontawesome` · `google-material` · `ionicons` · `lucide` · `material` · `meteocons` · `remix` · `rpg-awesome` · `simple` · `typicons` · `weather`

Sizes, styles, and glyph counts for each: **[the packs page](https://israel-dryer.github.io/tkinter-icons/packs.html)**.

There is deliberately no `[all]` extra — the sets serve disjoint purposes, so installing every one would cost about 17 MB to supply fifteen sets you never open.

## What you get

- **One API across every pack.** Each pack's class takes the same `(name, size, color, style)`, so switching sets is a one-line change.
- **Sharp at any size.** Glyphs are centered on measured ink rather than the font's own bounding box, which under-reports it. Odd sizes snap even; small sizes oversample and downscale.
- **Renders without a display.** `Icon.render_pil()` returns a Pillow image and touches no Tk — usable in tests, build steps, and server processes.
- **Follows your ttk theme.** `icon.map(widget)` tints the icon per widget state and re-renders it when the theme changes.
- **An icon browser.** Run `tkinter-icons` to search every installed set and copy the name you need.

## Documentation

- [Getting started](https://israel-dryer.github.io/tkinter-icons/getting-started.html)
- [Icon packs](https://israel-dryer.github.io/tkinter-icons/packs.html)
- [Stateful icons](https://israel-dryer.github.io/tkinter-icons/guide/stateful-icons.html)
- [API reference](https://israel-dryer.github.io/tkinter-icons/api.html)
- [Repository](https://github.com/israel-dryer/tkinter-icons)

## Upgrading from ttkbootstrap-icons

This package was published as `ttkbootstrap-icons` through 4.0.0. Installing that name still works — it is now a forwarding shim — and [the migration notes](https://israel-dryer.github.io/tkinter-icons/getting-started.html#migrating) cover the two things that genuinely changed.

## License

MIT for the library. Each pack redistributes an upstream icon font under that project's own license, shipped inside the pack; see [THIRD-PARTY-NOTICES.md](https://github.com/israel-dryer/tkinter-icons/blob/main/THIRD-PARTY-NOTICES.md).
