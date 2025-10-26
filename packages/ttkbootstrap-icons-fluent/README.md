# ttkbootstrap-icons-fluent

Fluent System Icons provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-fluent
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_fluent import FluentIcon

root = tk.Tk()

regular = FluentIcon("home-16-regular", 24, "#6f42c1", style="regular")
filled = FluentIcon("home-16-filled", 24, "#6f42c1", style="filled")

tk.Button(root, image=regular.image, text="Regular", compound="left").pack()
tk.Button(root, image=filled.image, text="Filled", compound="left").pack()

root.mainloop()
```

This package registers a provider entry point, so the base icon previewer will automatically discover it.

## Generate assets (developer)

```bash
# Quick build (Regular + Filled, and tries Light if available)
ttkicons-fluent-quick

# Preset build for a specific version (Regular)
ttkicons-fluent-build --preset fluent-regular --version 1.1.261

# Or direct URL to the zip (the tool extracts .ttf automatically)
ttkicons-fluent-build --font-url https://github.com/microsoft/fluentui-system-icons/releases/download/v1.1.261/FluentSystemIcons-Font.zip
```

Omitting metadata uses TTF-only extraction (needs `fonttools`).
