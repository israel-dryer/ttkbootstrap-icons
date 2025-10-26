# ttkbootstrap-icons-ion

Ion Icons provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-ion
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_ion import IonIcon

root = tk.Tk()

icon = IonIcon("home", size=24, color="#198754")
tk.Button(root, image=icon.image).pack()

root.mainloop()
```

This package registers a provider entry point, so the base icon previewer will automatically discover it.

## Generate assets (developer)

```bash
# Preset for Ionicons v2 font via cdnjs (automatically fetches CSS for readable names)
ttkicons-ion-build --preset ion2 --version 2.0.1

# Or direct URL
ttkicons-ion-build --font-url https://cdnjs.cloudflare.com/ajax/libs/ionicons/2.0.1/fonts/ionicons.ttf
```

Readable names
- The builder will try to fetch the matching CSS (ionicons.min.css) to map class names (e.g., `.ion-alert`) to codepoints.
- You can explicitly pass a CSS source:

```bash
ttkicons-ion-build \
  --font-url https://cdnjs.cloudflare.com/ajax/libs/ionicons/2.0.1/fonts/ionicons.ttf \
  --css-url  https://cdnjs.cloudflare.com/ajax/libs/ionicons/2.0.1/css/ionicons.min.css
```

Omitting metadata uses TTF-only extraction (needs `fonttools`).
