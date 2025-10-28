# Font Awesome (ttkbootstrap-icons-fa)

Font Awesome Free provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-fa
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Info

- Name: Font Awesome Free
- Icon Version (preset default): 6.5.2
- Source: https://fontawesome.com/ (CDN: https://cdnjs.com/libraries/font-awesome)

## License and Attribution

- Fonts: SIL Open Font License 1.1 (OFL-1.1)
- Code (CSS/JS): MIT License
- Icon designs: Creative Commons Attribution 4.0 (CC BY 4.0)
- Attribution: Font Awesome — https://fontawesome.com/

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_fa import FAIcon

root = tk.Tk()

# Solid (default)
solid = FAIcon("house", size=24, color="#0d6efd", style="solid")
# Regular
regular = FAIcon("house", size=24, color="#0d6efd", style="regular")
# Brands
brand = FAIcon("github", size=24, color="#0d6efd", style="brands")

tk.Button(root, image=solid.image, text="Solid", compound="left").pack()
tk.Button(root, image=regular.image, text="Regular", compound="left").pack()
tk.Button(root, image=brand.image, text="Brand", compound="left").pack()

root.mainloop()
```

This package registers a provider entry point, so the base icon previewer will automatically discover it.

## Generate assets (developer)

Use the bundled tool to fetch a TTF and produce `glyphmap.json`:

```bash
# Use a preset (Font Awesome 6 Free Solid via cdnjs)
ttkicons-fa-build --preset fa6-solid --version 6.5.2

# Or specify a direct URL
ttkicons-fa-build --font-url https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/webfonts/fa-solid-900.ttf

# Optional: supply metadata if you have it
ttkicons-fa-build --font-url ... --map-url https://example.com/metadata.json
```

If you omit metadata, the tool attempts to derive the glyphmap from the TTF (requires `fonttools`).

Styles
- This provider supports `style` values: `solid` (default), `regular`, `brands`.
- Ensure the following fonts are present in `fonts/` for full coverage:
  - `fa-solid-900.ttf`, `fa-regular-400.ttf`, `fa-brands-400.ttf`

## Changelog

| Version | Date       | Notes                                                    |
|--------:|------------|----------------------------------------------------------|
| 0.2.0   | 2025-10-28 | Typed `style` parameter (`solid`/`regular`/`brands`)     |
| 0.1.0   | 2024-10-27 | Initial provider and asset tooling available             |
