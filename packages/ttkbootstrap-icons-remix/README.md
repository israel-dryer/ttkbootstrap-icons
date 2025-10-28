# Remix Icon (ttkbootstrap-icons-remix)

Remix Icons provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-remix
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Info

- Name: Remix Icon
- Icon Version (preset default): 3.5.0
- Source: https://remixicon.com/ (npm: remixicon)

## License and Attribution

- Icons and code: Apache License 2.0
- Attribution: Remix Icon — https://remixicon.com/

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_remix import RemixIcon

root = tk.Tk()

icon = RemixIcon("home-3-fill", size=24, color="#fd7e14")
tk.Label(root, image=icon.image).pack()

root.mainloop()
```

This package registers a provider entry point, so the base icon previewer will automatically discover it.

## Generate assets (developer)

```bash
# Preset for Remix Icon via jsdelivr
ttkicons-remix-build --preset remix3 --version 3.5.0

# Or direct URL
ttkicons-remix-build --font-url https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.ttf
```

Omitting metadata uses TTF-only extraction (needs `fonttools`).

## Changelog

| Version | Date       | Notes                                 |
|--------:|------------|---------------------------------------|
| 0.2.0   | 2025-10-28 | Docs consistency; previewer UX tweaks |
| 0.1.0   | 2024-10-27 | Initial provider and basic usage docs |
