# RPG Awesome (ttkbootstrap-icons-rpga)

RPG Awesome provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-rpga
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Info

- Name: RPG Awesome
- Source: https://github.com/nagoshiashumari/Rpg-Awesome (CDN: https://cdnjs.com/libraries/rpg-awesome)
- Class prefix: `ra-`

## License and Attribution

- Icons and code: MIT License (per repository license)
- Attribution: RPG Awesome — https://nagoshiashumari.github.io/Rpg-Awesome/

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_rpga import RPGAIcon

root = tk.Tk()

# Both base and prefixed names work: "sword" or "ra-sword"
icon = RPGAIcon("sword", size=24, color="#6f42c1")
tk.Button(root, image=icon.image, text="Sword", compound="left").pack()

root.mainloop()
```

This package registers a provider entry point, so the base icon previewer will automatically discover it.

## Generate assets (developer)

Use the bundled tool to fetch the TTF and produce `glyphmap.json` with readable names from upstream CSS:

```bash
# Use preset (pulls TTF and CSS from cdnjs)
ttkicons-rpga-build --preset rpga --version 0.2.0

# Or specify sources directly
ttkicons-rpga-build \
  --font-url https://cdnjs.cloudflare.com/ajax/libs/rpg-awesome/0.2.0/fonts/rpgawesome-webfont.ttf \
  --css-url  https://cdnjs.cloudflare.com/ajax/libs/rpg-awesome/0.2.0/css/rpg-awesome.min.css
```

If CSS is unavailable, the tool falls back to deriving a glyph map from the TTF (requires `fonttools`).

## Changelog

| Version | Date       | Notes                                                       |
|--------:|------------|-------------------------------------------------------------|
| 0.1.0   | 2025-10-28 | Initial provider; CSS/TTF builder preset; `ra-` class map   |
