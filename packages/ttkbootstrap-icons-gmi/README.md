# Material Icons (ttkbootstrap-icons-gmi)

Google Material Icons provider (baseline/outlined/round/sharp/twotone) for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-gmi
```

Requires `ttkbootstrap-icons` and `Pillow`.

## Info

- Name: Material Icons
- Icon Version (preset default): latest
- Source: https://github.com/google/material-design-icons

## License and Attribution

- Icons and code: Apache License 2.0 (per material-design-icons repository)
- Attribution: Google Material Icons — https://fonts.google.com/icons

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_gmi import GMIIcon

root = tk.Tk()

base = GMIIcon("home", 24, "#555", style="baseline")
outlined = GMIIcon("home", 24, "#555", style="outlined")
rounded = GMIIcon("home", 24, "#555", style="round")
sharp = GMIIcon("home", 24, "#555", style="sharp")
twotone = GMIIcon("home", 24, "#555", style="twotone")

for lbl, icon in [
    ("Baseline", base), ("Outlined", outlined), ("Round", rounded), ("Sharp", sharp), ("TwoTone", twotone)
]:
    tk.Button(root, image=icon.image, text=lbl, compound="left").pack()

root.mainloop()
```

## Build assets (maintainers)

```bash
# Quick build: downloads fonts and codepoints; writes glyphmap.json
ttkicons-gmi-quick

# Full builder
ttkicons-gmi-build --preset gmi --version latest
```
