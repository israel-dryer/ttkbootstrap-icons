# ttkbootstrap-icons-mat

Material Icons provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-mat
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

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
