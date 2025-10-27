# Lucide Icons (ttkbootstrap-icons-lucide)

Lucide Icons provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-lucide
```

Requires `ttkbootstrap-icons` and `Pillow`.

## Info

- Name: Lucide Icons
- Icon Version: see lucide.dev (varies)
- Source: https://lucide.dev/

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_lucide import LucideIcon

root = tk.Tk()

icon = LucideIcon("home", size=24, color="#333")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()

root.mainloop()
```

## Generate assets (developer)

```bash
# Quick build (uses preset defaults if configured)
ttkicons-lucide-quick

# Full build (download JSON + font and write glyphmap.json)
ttkicons-lucide-build
```

