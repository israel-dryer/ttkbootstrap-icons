# Fluent System Icons (ttkbootstrap-icons-fluent)

Fluent System Icons provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-fluent
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Info

- Name: Fluent System Icons
- Icon Version (preset default): 1.1.261 (example)
- Source: https://github.com/microsoft/fluentui-system-icons

## License and Attribution

- Icons and code: MIT License (per repository license)
- Attribution: Microsoft Fluent UI System Icons — https://github.com/microsoft/fluentui-system-icons

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_fluent import FluentIcon

root = tk.Tk()

regular = FluentIcon("home-16", size=24, color="#6f42c1", style="regular")
filled = FluentIcon("home-16", size=24, color="#6f42c1", style="filled")

tk.Button(root, image=regular.image, text="Regular", compound="left").pack()
tk.Button(root, image=filled.image, text="Filled", compound="left").pack()

root.mainloop()
```

This package registers a provider entry point, so the base icon previewer will automatically discover it.

### Styles

- Supported styles: `regular`, `filled`, `light` (if the Light font is present)
- You may also pass fully-qualified names (e.g., `home-16-filled`). If the style suffix is missing, it is appended automatically based on the provided `style` parameter.
- The previewer shows base names with a Style dropdown; copying an icon copies the base name. Use it with the chosen style in code for clarity.

## Generate assets (developer)

```bash
# Quick build (Regular + Filled, and tries Light if available)
ttkicons-fluent-quick

# Preset build for a specific version (Regular)
ttkicons-fluent-build --preset fluent-regular --version 1.1.261

# Or direct URL to the zip (the tool extracts .ttf automatically)
ttkicons-fluent-build --font-url https://github.com/microsoft/fluentui-system-icons/releases/download/v1.1.261/FluentSystemIcons-Font.zip
```

Notes
- The quick build writes per-style glyph maps when possible (e.g., `glyphmap-regular.json`, `glyphmap-filled.json`, and `glyphmap-light.json` when available). The provider will use the style-specific map for better name coverage.
- Omitting metadata uses TTF-only extraction (needs `fonttools`).

## Changelog

| Version | Date       | Notes                                                                                                   |
|--------:|------------|---------------------------------------------------------------------------------------------------------|
| 0.2.0   | 2025-10-28 | Per-style glyphmaps written and used; previewer shows base names, appends suffix; typed `style` union   |
| 0.1.0   | 2024-10-27 | Initial provider; per-style glyphmaps support; previewer shows base names with a separate style param   |
