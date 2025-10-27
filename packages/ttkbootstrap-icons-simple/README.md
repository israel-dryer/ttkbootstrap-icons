# Simple Icons (ttkbootstrap-icons-simple)

Simple Icons provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-simple
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Info

- Name: Simple Icons Font (community)
- Icon Version (preset default): latest
- Source: https://github.com/simple-icons/simple-icons-font

## License and Attribution

- Underlying icon set: Simple Icons — CC0 1.0 Universal (public domain) — https://simpleicons.org/
- This font project: see the simple-icons-font repository for license details (often MIT for code)
- Attribution: Simple Icons — https://simpleicons.org/

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_simple import SimpleIcon

root = tk.Tk()

icon = SimpleIcon("python", size=24, color="#333333")
tk.Label(root, image=icon.image).pack()

root.mainloop()
```

This package registers a provider entry point, so the base icon previewer will automatically discover it.

## Generate assets (developer)

```bash
# Provide a direct URL to a community TTF (no official preset)
ttkicons-simple-build --font-url https://example.com/path/to/simple-icons.ttf
```

Omitting metadata uses TTF-only extraction (needs `fonttools`).
