# Devicon (ttkbootstrap-icons-devicon)

Devicon provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-devicon
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Info

- Name: Devicon
- Source: https://devicon.dev (GitHub: https://github.com/devicons/devicon)
- Variants (font): original, original-wordmark; aliases: plain, plain-wordmark
  - Example names: `python-plain`, `python-plain-wordmark`, `react-original`

## License and Attribution

- License: MIT (Devicon)
- Attribution: Devicon — https://devicon.dev

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_devicon import DevIcon

root = tk.Tk()

py = DevIcon("python", size=24, color="#3776AB", style="plain")
re = DevIcon("react", size=24, color="#61dafb", style="original")

tk.Button(root, image=py.image, text="Python", compound="left").pack()
tk.Button(root, image=re.image, text="React", compound="left").pack()

root.mainloop()
```

This package registers a provider entry point, so the base icon previewer will automatically discover it.

## Generate assets (developer)

Use the bundled tool to fetch the TTF and produce `glyphmap.json` with readable names from upstream CSS/metadata:

```bash
# Use preset (pulls TTF, devicon.min.css/devicon-base.css, and devicon.json)
ttkicons-devicon-build --preset devicon

# Or specify sources directly
ttkicons-devicon-build \
  --font-url https://raw.githubusercontent.com/devicons/devicon/master/fonts/devicon.ttf \
  --css-url  https://raw.githubusercontent.com/devicons/devicon/master/devicon.min.css \
  --meta-url https://raw.githubusercontent.com/devicons/devicon/master/devicon.json
```

If CSS/metadata are unavailable, the tool falls back to deriving a glyph map from the TTF (requires `fonttools`).

### Aliases, styles, and convenience names

- Upstream aliases (e.g., `original` → `plain`) are expanded based on devicon.json.
- Styles are naming-level variants on a single font: `plain`, `plain-wordmark`, `original`, `original-wordmark`.
- You can supply either full names (e.g., `python-plain`) or a base name with a `style` parameter.
- A convenience alias `name` → `name-plain` is added when applicable.

## Changelog

| Version | Date       | Notes                                                                                                      |
|--------:|------------|------------------------------------------------------------------------------------------------------------|
| 0.2.0   | 2025-10-28 | Previewer shows base names with Style dropdown; generator uses devicon-base.css + devicon.json; typed style |
| 0.1.0   | 2024-10-27 | Initial provider; style variants exposed via `style`; CSS/metadata map                                      |
