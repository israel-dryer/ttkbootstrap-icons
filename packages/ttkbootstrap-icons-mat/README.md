# Material Design Icons (ttkbootstrap-icons-mat)

Material Icons provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-mat
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Info

- Name: Material Design Icons (MDI)
- Icon Version (preset default): 7.4.47
- Source: https://github.com/Templarian/MaterialDesign-Webfont (npm: @mdi/font)

## License and Attribution

- Icons and code: Apache License 2.0
- Attribution: Material Design Icons — https://materialdesignicons.com/ and @mdi/font

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_mat import MatIcon

root = tk.Tk()

icon = MatIcon("home", size=24, color="#dc3545")
tk.Label(root, image=icon.image).pack()

root.mainloop()
```

This package registers a provider entry point, so the base icon previewer will automatically discover it.

## Generate assets (developer)

```bash
# Use preset for Material Design Icons (MDI) via jsdelivr
ttkicons-mat-build --preset mdi --version 7.4.47

# Or direct URL
ttkicons-mat-build --font-url https://cdn.jsdelivr.net/npm/@mdi/font@7.4.47/fonts/materialdesignicons-webfont.ttf
```

Omitting metadata uses TTF-only extraction (needs `fonttools`).

## Changelog

| Version | Date       | Notes                                 |
|--------:|------------|---------------------------------------|
| 0.2.0   | 2025-10-28 | Docs consistency; previewer UX tweaks |
| 0.1.0   | 2024-10-27 | Initial provider and basic usage docs |
