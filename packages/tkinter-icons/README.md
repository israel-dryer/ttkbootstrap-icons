<picture>
  <source media="(prefers-color-scheme: dark)"
          srcset="https://raw.githubusercontent.com/israel-dryer/tkinter-icons/main/assets/png/wordmark-dark.png">
  <img alt="tkinter-icons"
       src="https://raw.githubusercontent.com/israel-dryer/tkinter-icons/main/assets/png/wordmark-light.png"
       width="420">
</picture>

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons.svg)](https://pypi.org/project/tkinter-icons/)
[![Python Versions](https://img.shields.io/pypi/pyversions/tkinter-icons.svg)](https://pypi.org/project/tkinter-icons/)
[![Downloads](https://static.pepy.tech/badge/tkinter-icons)](https://pepy.tech/project/tkinter-icons)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../../LICENSE)

Font-based icons for Tkinter — 61,000+ icons across sixteen sets, one import, no image files to manage.

## Install

One line puts a full icon set in your project:

```bash
pip install "tkinter-icons[material]"
```

```python
import tkinter as tk
from tkinter import ttk

from tkinter_icons import MaterialIcon

root = tk.Tk()

home = MaterialIcon("home", size=24, color="#0F766E")
ttk.Button(root, text="Home", image=home.image, compound="left").pack(padx=20, pady=20)

root.mainloop()
```

The quotes matter — most shells treat unquoted brackets as a glob. Name two packs together as `"tkinter-icons[material,simple]"`.

That is the whole model: one library, sixteen installable icon packs. The base package is the renderer; the glyphs come from the pack you named.

## The sixteen packs

`bootstrap` · `devicon` · `eva` · `fluent` · `fluent-regular` · `fontawesome` · `google-material` · `ionicons` · `lucide` · `material` · `meteocons` · `remix` · `rpg-awesome` · `simple` · `typicons` · `weather`

Sizes, styles, and glyph counts for each: **[the packs page](https://tkinter-icons.readthedocs.io/en/latest/packs.html)**.

## What you get

- **One API across every pack.** Each pack's class takes the same `(name, size, color, style)`, so switching sets is a one-line change.
- **Sharp at any size.** Glyphs are centered on measured ink rather than the font's own bounding box, which under-reports it. Odd sizes snap even; small sizes oversample and downscale.
- **No image assets to manage.** Size and color are arguments, not files. No `icons/` directory, no `@2x` duplicates, no second set for dark mode.
- **Follows your ttk theme.** `icon.map(widget)` tints the icon per widget state and re-renders it when the theme changes.
- **An icon browser.** Run `tkinter-icons` to search every installed set and copy the name you need.

## Documentation

- [Get started](https://tkinter-icons.readthedocs.io/en/latest/getting-started/installation.html)
- [Icon packs](https://tkinter-icons.readthedocs.io/en/latest/packs.html)
- [Stateful icons](https://tkinter-icons.readthedocs.io/en/latest/user-guide/stateful-icons.html)
- [API reference](https://tkinter-icons.readthedocs.io/en/latest/api.html)
- [Repository](https://github.com/israel-dryer/tkinter-icons)

## Upgrading from ttkbootstrap-icons

This package was published as `ttkbootstrap-icons` through 4.0.0. Installing that name still works — it is now a forwarding shim — and [the migration notes](https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html) cover the two things that genuinely changed.

## License

MIT for the library. Each pack redistributes an upstream icon font under that project's own license, shipped inside the pack; see [THIRD-PARTY-NOTICES.md](https://github.com/israel-dryer/tkinter-icons/blob/main/THIRD-PARTY-NOTICES.md).
