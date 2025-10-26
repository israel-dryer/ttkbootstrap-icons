# ttkbootstrap-icons-fa

Font Awesome Free provider for ttkbootstrap-icons.

## Install

```bash
pip install ttkbootstrap-icons-fa
```

Requires `ttkbootstrap-icons` (installed automatically) and `Pillow`.

## Usage

```python
import tkinter as tk
from ttkbootstrap_icons_fa import FAIcon

root = tk.Tk()

icon = FAIcon("house", size=24, color="#0d6efd")
btn = tk.Button(root, image=icon.image, text="FA House", compound="left")
btn.pack()

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
