# Eva Icons (ttkbootstrap-icons-eva)

Eva Icons provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-eva
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Info

// Name: Eva Icons

- Source: https://github.com/akveo/eva-icons (NPM: eva-icons)
- Variants (font): `outline`, `fill`

## License and Attribution

- Icons and code: MIT License (per repository license)
- Attribution: Eva Icons — https://akveo.github.io/eva-icons/

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_eva import EvaIcon

root = tk.Tk()

outline = EvaIcon("activity", size=24, color="#333", style="outline")
filled = EvaIcon("activity", size=24, color="#333", style="fill")

tk.Button(root, image=outline.image, text="Outline", compound="left").pack()
tk.Button(root, image=filled.image, text="Fill", compound="left").pack()

root.mainloop()
```

This package registers a provider entry point, so the base icon previewer will automatically discover it.

## Generate assets (developer)

Use the bundled tool to fetch the TTF and produce `glyphmap.json` with readable names from upstream CSS:

```bash
# Use preset (pulls TTF and CSS from unpkg)
ttkicons-eva-build --preset eva

# Or specify sources directly
ttkicons-eva-build \
  --font-url https://unpkg.com/eva-icons/fonts/eva-icons.ttf \
  --css-url  https://unpkg.com/eva-icons/style/eva-icons.css
```

If CSS is unavailable, the tool falls back to deriving a glyph map from the TTF (requires `fonttools`).

### Styles

- Supported styles: `outline`, `fill`
- Eva encodes fill as the base name (e.g., `archive`), and outline with a `-outline` suffix (e.g., `archive-outline`).
- `*-fill` is accepted as an alias and resolved to the base name (e.g., `archive-fill` → `archive`).
- Passing a style parameter without a suffix resolves as:
    - `style="fill"` → base name (e.g., `EvaIcon("archive", style="fill")` → `archive`).
    - `style="outline"` → `-outline` (e.g., `EvaIcon("archive", style="outline")` → `archive-outline`).
- Fully‑qualified names are honored as given.
- The previewer shows base names with a Style dropdown.

## Changelog

| Version | Date       | Notes                                                                                   |
|--------:|------------|-----------------------------------------------------------------------------------------|
|   0.2.0 | 2025-10-28 | Default style set to fill; improved name+style resolution (fill→base, outline→-outline) |
|   0.1.0 | 2025-10-28 | Initial provider; style variants via parameter; CSS/TTF builder preset                  |
