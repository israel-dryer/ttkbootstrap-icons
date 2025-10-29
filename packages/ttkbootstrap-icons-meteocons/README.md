# Meteocons (ttkbootstrap-icons-meteocons)

Meteocons provider for ttkbootstrap-icons.

Icon reference and live preview: https://demo.alessioatzeni.com/meteocons/#

## Install

```bash
pip install ttkbootstrap-icons-meteocons
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Info

- Name: Meteocons
- Source: https://github.com/fontello/meteocons.font
- Demo: https://demo.alessioatzeni.com/meteocons/#

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_meteocons import MeteoconsIcon

root = tk.Tk()

icon = MeteoconsIcon("a", size=24, color="#0077ff")
tk.Button(root, image=icon.image, text="Meteocons", compound="left").pack()

root.mainloop()
```

Assets (font + glyphmap) are bundled with the package. No build steps are
required for end users.

## Generate assets (developer)

Only needed when updating to a newer upstream font.

```bash
# From a local font file
python -m ttkbootstrap_icons_meteocons.tools.generate_assets --font-file path/to/meteocons.ttf

# (Optional) Attempt to fetch from upstream preset
python -m ttkbootstrap_icons_meteocons.tools.generate_assets --preset fontello
```

The generator derives names from the font cmap and filters whitespace/blank
glyphs. Results are written to `glyphmap.json` under the package.

## License

See upstream project for icon licensing. This package provides integration for
use with Tkinter; the icon set remains under its original license.

## Changelog

| Version | Date       | Notes                                 |
|--------:|------------|---------------------------------------|
| 0.1.0   | 2025-10-28 | Initial provider and basic usage docs |
