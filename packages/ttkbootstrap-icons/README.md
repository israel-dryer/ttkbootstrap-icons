# ttkbootstrap-icons

A Python package for using Bootstrap and Lucide icons in your tkinter/ttkbootstrap applications — now with plug-in
providers (Font Awesome, Material, Ion, Remix, Fluent, Simple, Weather) available as optional subpackages.

![Icon Previewer](https://raw.githubusercontent.com/israel-dryer/ttkbootstrap-icons/main/examples/previewer.png)

## Features

- Built-in set: Bootstrap Icons
- Pluggable providers: Font Awesome, Material (MDI), Ionicons, Remix, Fluent, Simple, Weather
- Style variants: Style-aware rendering for sets that provide them (e.g., Font Awesome solid/regular/brands; Fluent
  regular/filled/light; Google Material baseline/outlined/round/sharp/twotone)
- Readable names: CSS-based name mapping for font sets (Ionicons, MDI, Remix, Weather, Simple) for human-friendly icon
  names in the previewer
- Previewer: Auto-discovers installed providers, offers a Style combobox when available, fast virtual scroll, search,
  size and color controls, click-to-copy
- Font-based rendering using Pillow; cross-platform (Windows/macOS/Linux)
- PyInstaller support with included hook for bundling assets

**Providers Summary**

- [Bootstrap Icons](https://icons.getbootstrap.com/)

## Installation

```bash
pip install ttkbootstrap-icons
```

Optional providers (install any you want):

```bash
pip install ttkbootstrap-icons-fa       # Font Awesome (Free)
pip install ttkbootstrap-icons-mat      # Material Icons
pip install ttkbootstrap-icons-ion      # Ion Icons
pip install ttkbootstrap-icons-remix    # Remix Icons
pip install ttkbootstrap-icons-fluent   # Fluent System Icons
pip install ttkbootstrap-icons-simple   # Simple Icons
pip install ttkbootstrap-icons-weather  # Weather Icons
```

## Quick Start

### Bootstrap Icons

```python
import tkinter as tk
from ttkbootstrap_icons import BootstrapIcon

root = tk.Tk()

# Create a Bootstrap icon
icon = BootstrapIcon("house", size=32, color="blue")

# Use it in a label
label = tk.Label(root, image=icon.image)
label.pack()

root.mainloop()
```

### Lucide Icons

```python
import tkinter as tk
from ttkbootstrap_icons import LucideIcon

root = tk.Tk()

# Create a Lucide icon
icon = LucideIcon("home", size=32, color="red")

# Use it in a button
button = tk.Button(root, image=icon.image, text="Home", compound="left")
button.pack()

root.mainloop()
```

### Provider Icons (Font Awesome, Material, …)

Install the provider package, then import and use its convenience icon class:

```python
import tkinter as tk
from ttkbootstrap_icons_fa import FAIcon  # Font Awesome (Free)
from ttkbootstrap_icons_mat import MatIcon  # Material Icons

root = tk.Tk()

fa = FAIcon("house", size=24, color="#0d6efd")
mat = MatIcon("home", size=24, color="#dc3545")

tk.Button(root, image=fa.image, text="FA House", compound="left").pack()
tk.Button(root, image=mat.image, text="Mat Home", compound="left").pack()

root.mainloop()
```

Other provider classes you can import similarly after installing their packages:

- `from ttkbootstrap_icons_ion import IonIcon`
- `from ttkbootstrap_icons_remix import RemixIcon`
- `from ttkbootstrap_icons_fluent import FluentIcon`
- `from ttkbootstrap_icons_simple import SimpleIcon`
- `from ttkbootstrap_icons_weather import WeatherIcon`

## API Reference

### BootstrapIcon

```python
BootstrapIcon(name: str, size: int = 24, color: str = "black")
```

**Parameters:**

- `name`: The name of the Bootstrap icon (e.g., "house", "search", "heart")
- `size`: Size of the icon in pixels (default: 24)
- `color`: Color of the icon (default: "black"). Accepts any valid Tkinter color string

**Attributes:**

- `image`: Returns the PhotoImage object that can be used in Tkinter widgets

### LucideIcon

```python
LucideIcon(name: str, size: int = 24, color: str = "black")
```

**Parameters:**

- `name`: The name of the Lucide icon (e.g., "home", "settings", "user")
- `size`: Size of the icon in pixels (default: 24)
- `color`: Color of the icon (default: "black"). Accepts any valid Tkinter color string

**Attributes:**

- `image`: Returns the PhotoImage object that can be used in Tkinter widgets

## Available Icons

- **Bootstrap Icons**: See the [Bootstrap Icons website](https://icons.getbootstrap.com/) for a full list of available
  icons
- **Lucide Icons**: See the [Lucide Icons website](https://lucide.dev/) for a full list of available icons

## Advanced Usage

### Using Icons in Different Widgets

```python
from ttkbootstrap_icons import BootstrapIcon, LucideIcon
import tkinter as tk

root = tk.Tk()

# In a Button
icon1 = BootstrapIcon("gear", size=24, color="#333333")
btn = tk.Button(root, image=icon1.image, text="Settings", compound="left")
btn.pack()

# In a Label
icon2 = LucideIcon("alert-circle", size=48, color="orange")
lbl = tk.Label(root, image=icon2.image)
lbl.pack()

# Keep references to avoid garbage collection
root.icon1 = icon1
root.icon2 = icon2

root.mainloop()
```

### Transparent Icons

You can create a transparent placeholder icon using the special name "none":

```python
transparent_icon = BootstrapIcon("none", size=24)
```

## Examples

The repository includes example applications demonstrating various use cases. These are available in
the [examples directory](https://github.com/israel-dryer/ttkbootstrap-icons/tree/main/examples) on GitHub.

### Basic Example

A simple application showing both Bootstrap and Lucide icons in buttons:

```python
import atexit
import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons import BootstrapIcon, LucideIcon
from ttkbootstrap_icons import Icon


def main():
    # Register cleanup to remove temporary font files on exit
    atexit.register(Icon.cleanup)

    root = tk.Tk()
    root.title("ttkbootstrap-icons Example")

    # Title
    title = tk.Label(root, text="Icon Examples", font=("Arial", 16, "bold"))
    title.pack(pady=10)

    # Bootstrap Icons
    frame1 = ttk.LabelFrame(root, text="Bootstrap Icons", padding=10)
    frame1.pack(fill="x", padx=20, pady=10)

    icons = [
        ("house", "Home"),
        ("gear", "Settings"),
        ("heart", "Favorite"),
        ("search", "Search"),
    ]

    for icon_name, label_text in icons:
        icon = BootstrapIcon(icon_name, size=24, color="#0d6efd")
        btn = tk.Button(
            frame1, image=icon.image, text=label_text, compound="left", width=120
        )
        btn.pack(side="left", padx=5)
        # Keep reference to prevent garbage collection
        btn.icon = icon

    # Lucide Icons
    frame2 = ttk.LabelFrame(root, text="Lucide Icons", padding=10)
    frame2.pack(fill="x", padx=20, pady=10)

    lucide_icons = [
        ("house", "Home"),
        ("settings", "Settings"),
        ("user", "User"),
        ("bell", "Notifications"),
    ]

    for icon_name, label_text in lucide_icons:
        icon = LucideIcon(icon_name, size=24, color="#dc3545")
        btn = tk.Button(
            frame2, image=icon.image, text=label_text, compound="left", width=120
        )
        btn.pack(side="left", padx=5)
        # Keep reference to prevent garbage collection
        btn.icon = icon

    # Info
    info = tk.Label(
        root,
        text="Icons are rendered from fonts and can be any size/color!",
        font=("Arial", 9),
        fg="gray",
    )
    info.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
```

![Example Application](https://raw.githubusercontent.com/israel-dryer/ttkbootstrap-icons/main/examples/example.png)

### Running Examples Locally

Clone the repository and run the examples:

```bash
git clone https://github.com/israel-dryer/ttkbootstrap-icons.git
cd ttkbootstrap-icons
pip install -e .
python example.py
```

## Icon Previewer

The package includes an interactive icon previewer application to browse all available icons. It automatically discovers
any installed provider packages and adds them to the icon set list.

### Using the CLI Command

After installing the package:

```bash
ttkbootstrap-icons
```

### Alternative Methods

Run directly with Python:

```bash
python -m ttkbootstrap_icons.icon_previewer
```

For development (from the repository root):

```bash
pip install -e .
ttkbootstrap-icons
```

**Features:**

- Browse built-in (Bootstrap, Lucide) and any installed provider sets
- Real-time search filtering
- Adjustable icon size (16-128px)
- Color customization with presets
- Virtual scrolling for smooth performance
- Fixed 800x600 window

**Controls:**

- **Icon Set**: Switch between Bootstrap and Lucide icon sets
- **Search**: Filter icons by name (case-insensitive)
- **Size**: Adjust preview size from 16 to 128 pixels
- **Color**: Enter any valid Tkinter color (hex codes, names, etc.)
- **Color Presets**: Quick color selection buttons
- **Click to Copy**: Click any icon to copy its name to clipboard

![Icon Previewer](https://raw.githubusercontent.com/israel-dryer/ttkbootstrap-icons/main/examples/previewer.png)

Perfect for discovering the right icon for your project!

## Using with PyInstaller

This package includes built-in PyInstaller support. The icon assets (fonts and metadata) will be automatically included
when you freeze your application.

### Basic Usage

```bash
pip install pyinstaller
pyinstaller --onefile your_app.py
```

### With Hook Directory (Automatic)

The package includes a PyInstaller hook that automatically bundles the required assets. In most cases, PyInstaller will
detect and use this hook automatically.

### Manual Hook Configuration (If Needed)

If the automatic detection doesn't work, you can manually specify the hook directory:

```python
# your_app.spec file or command line
pyinstaller - -additional - hooks - dir = path / to / site - packages / ttkbootstrap_icons / _pyinstaller
your_app.py
```

Or in your `.spec` file:

```python
a = Analysis(
    ['your_app.py'],
    ...
hookspath = ['path/to/site-packages/ttkbootstrap_icons/_pyinstaller'],
...
)
```

### Programmatic Hook Discovery

```python
from ttkbootstrap_icons import get_hook_dirs

# Use in your build script
hook_dirs = get_hook_dirs()
```

### Testing Your Frozen Application

After building with PyInstaller, test that icons load correctly:

```bash
./dist/your_app  # Linux/Mac
dist\your_app.exe  # Windows
```

### Cleanup Temporary Files

Icons create temporary font files. To clean them up when your app exits:

```python
import atexit
from ttkbootstrap_icons import Icon

# Register cleanup on exit
atexit.register(Icon.cleanup)
```

## Requirements

- Python >= 3.10
- Pillow >= 9.0.0

## Maintainers

The following tools are intended for library maintainers to (re)build provider assets (fonts + glyphmap). End users do
not need these commands to use icons.

- Build all installed providers using recommended presets:

    - `ttkicons-build-all`
    - Options:
        - `--only fa ion remix` to limit which providers run
        - `--dry-run` to list providers without building

- Per‑provider quick builders (no parameters):

    - `ttkicons-fa-quick` (Font Awesome 6 Free Solid)
    - `ttkicons-mat-quick` (Material Design Icons webfont)
    - `ttkicons-ion-quick` (Ionicons v2)
    - `ttkicons-remix-quick` (Remix Icon)
    - `ttkicons-fluent-quick` (Fluent System Icons Regular)
    - `ttkicons-weather-quick` (Weather Icons)

- Per‑provider full builders (custom sources):

    - `ttkicons-fa-build --preset fa6-solid --version 6.5.2`
    - `ttkicons-fa-build --font-url https://…/fa-solid-900.ttf --map-url https://…/metadata.json`

Notes:

- Builders write into each provider package directory under `fonts/` and `glyphmap.json`.
- If no metadata JSON is supplied, glyph maps are derived from the TTF’s cmap and require `fonttools` (
  `pip install fonttools`).
- Respect upstream licenses when downloading and distributing fonts and metadata.

## License

MIT License - see LICENSE file for details

## Author

Israel Dryer (israel.dryer@gmail.com)

## Links

- [GitHub Repository](https://github.com/israel-dryer/ttkbootstrap-icons)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Lucide Icons](https://lucide.dev/)
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/)

# ttkbootstrap-icons (Bootstrap built-in, providers optional)

Font-based icons for Tkinter/ttkbootstrap with a built-in Bootstrap set and installable providers: Font Awesome, Material (MDI), Ionicons, Remix, Fluent, Simple, Weather, Lucide.

![Icon Previewer](https://raw.githubusercontent.com/israel-dryer/ttkbootstrap-icons/main/examples/previewer.png)

## Key Features

- Built-in set: Bootstrap Icons
- Pluggable providers: Font Awesome, Material (MDI), Ionicons, Remix, Fluent, Simple, Weather, Lucide
- Style variants where available (e.g., Font Awesome solid/regular/brands; Fluent regular/filled/light; Google Material baseline/outlined/round/sharp/twotone)
- Readable icon names via CSS mapping for font sets (Ionicons, MDI, Remix, Weather, Simple)
- Previewer app: search, style selector, size/color controls, click-to-copy; auto-discovers installed providers
- Works cross‑platform; ships a PyInstaller hook for bundling assets

## Installation

Base package (Bootstrap Icons built-in):

```bash
pip install ttkbootstrap-icons
```

Optional providers (install any you want):

```bash
pip install ttkbootstrap-icons-fa       # Font Awesome (Free)
pip install ttkbootstrap-icons-mat      # Material Design Icons (MDI)
pip install ttkbootstrap-icons-ion      # Ionicons v2 (font)
pip install ttkbootstrap-icons-remix    # Remix Icon
pip install ttkbootstrap-icons-fluent   # Fluent System Icons
pip install ttkbootstrap-icons-simple   # Simple Icons (community font)
pip install ttkbootstrap-icons-weather  # Weather Icons
pip install ttkbootstrap-icons-lucide   # Lucide Icons
pip install ttkbootstrap-icons-gmi      # Google Material Icons (baseline/outlined/round/sharp/twotone)
```

## Usage

Bootstrap (built-in):

```python
import tkinter as tk
from ttkbootstrap_icons import BootstrapIcon

root = tk.Tk()
icon = BootstrapIcon("house", size=24, color="#0d6efd")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()
root.mainloop()
```

Providers (examples):

```python
import tkinter as tk
from ttkbootstrap_icons_fa import FAIcon            # Font Awesome
from ttkbootstrap_icons_mat import MatIcon          # Material (MDI)
from ttkbootstrap_icons_fluent import FluentIcon    # Fluent (style-aware)

root = tk.Tk()

tk.Button(root, image=FAIcon("house", 24, "#0d6efd", style="solid").image,
          text="FA Solid", compound="left").pack()

tk.Button(root, image=MatIcon("home", 24, "#dc3545").image,
          text="MDI", compound="left").pack()

tk.Button(root, image=FluentIcon("home-16", 24, "#6f42c1", style="filled").image,
          text="Fluent Filled", compound="left").pack()

root.mainloop()
```

Previewer:

```bash
ttkbootstrap-icons
```

## Providers (sorted)

- [Bootstrap Icons](https://icons.getbootstrap.com/)
  - Package: `ttkbootstrap-icons` (built-in)
  - Styles: n/a
  - Version: bundled
  - Source: icons.getbootstrap.com
  - License: MIT (code), OFL 1.1 (font)

- [Fluent System Icons](https://github.com/israel-dryer/ttkbootstrap-icons/tree/main/packages/ttkbootstrap-icons-fluent)
  - Package: `ttkbootstrap-icons-fluent`
  - Install: `pip install ttkbootstrap-icons-fluent`
  - Styles: regular, filled, light
  - Preset version: 1.1.261 (example)
  - Source: github.com/microsoft/fluentui-system-icons
  - License: MIT

- [Font Awesome Free](https://github.com/israel-dryer/ttkbootstrap-icons/tree/main/packages/ttkbootstrap-icons-fa)
  - Package: `ttkbootstrap-icons-fa`
  - Install: `pip install ttkbootstrap-icons-fa`
  - Styles: solid, regular, brands
  - Preset version: 6.5.2
  - Source: fontawesome.com (CDNJS)
  - License: OFL 1.1 (fonts), MIT (code), CC BY 4.0 (designs)

- [Ionicons v2 (font)](https://github.com/israel-dryer/ttkbootstrap-icons/tree/main/packages/ttkbootstrap-icons-ion)
  - Package: `ttkbootstrap-icons-ion`
  - Install: `pip install ttkbootstrap-icons-ion`
  - Styles: n/a (ios-/md- variants appear as friendly names in previewer)
  - Preset version: 2.0.1
  - Source: ionic.io/ionicons (CDNJS)
  - License: MIT

- [Lucide Icons](https://github.com/israel-dryer/ttkbootstrap-icons/tree/main/packages/ttkbootstrap-icons-lucide)
  - Package: `ttkbootstrap-icons-lucide`
  - Install: `pip install ttkbootstrap-icons-lucide`
  - Styles: n/a
  - Version: see lucide.dev (varies)
  - Source: lucide.dev
  - License: ISC/MIT (project)

- [Material Design Icons (MDI)](https://github.com/israel-dryer/ttkbootstrap-icons/tree/main/packages/ttkbootstrap-icons-mat)
  - Package: `ttkbootstrap-icons-mat`
  - Install: `pip install ttkbootstrap-icons-mat`
  - Styles: n/a (outline/variants in names, e.g., home-outline)
  - Preset version: 7.4.47
  - Source: github.com/Templarian/MaterialDesign-Webfont
  - License: Apache 2.0

- [Material Icons (Google)](https://github.com/israel-dryer/ttkbootstrap-icons/tree/main/packages/ttkbootstrap-icons-gmi)
  - Package: `ttkbootstrap-icons-gmi`
  - Install: `pip install ttkbootstrap-icons-gmi`
  - Styles: baseline, outlined, round, sharp, twotone
  - Preset version: latest
  - Source: github.com/google/material-design-icons
  - License: Apache 2.0

- [Remix Icon](https://github.com/israel-dryer/ttkbootstrap-icons/tree/main/packages/ttkbootstrap-icons-remix)
  - Package: `ttkbootstrap-icons-remix`
  - Install: `pip install ttkbootstrap-icons-remix`
  - Styles: n/a
  - Preset version: 3.5.0
  - Source: remixicon.com
  - License: Apache 2.0

- [Simple Icons (community font)](https://github.com/israel-dryer/ttkbootstrap-icons/tree/main/packages/ttkbootstrap-icons-simple)
  - Package: `ttkbootstrap-icons-simple`
  - Install: `pip install ttkbootstrap-icons-simple`
  - Styles: n/a
  - Preset version: latest
  - Source: github.com/simple-icons/simple-icons-font
  - License: CC0 1.0 (underlying set), font project often MIT (see repo)

- [Weather Icons](https://github.com/israel-dryer/ttkbootstrap-icons/tree/main/packages/ttkbootstrap-icons-weather)
  - Package: `ttkbootstrap-icons-weather`
  - Install: `pip install ttkbootstrap-icons-weather`
  - Styles: n/a
  - Preset version: 2.0.10
  - Source: erikflowers.github.io/weather-icons (CDNJS)
  - License: OFL 1.1 (font), MIT (code), CC BY 3.0 (docs)

---

For bundling, Maintainer tools, PyInstaller instructions, and more examples, see the sections below in this README.
# ttkbootstrap-icons

Bootstrap Icons for Tkinter/ttkbootstrap with optional provider add‑ons.

This package ships Bootstrap Icons built‑in and provides the previewer CLI. For full documentation, provider details, and examples, see the root README: https://github.com/israel-dryer/ttkbootstrap-icons

## Install

Base package (Bootstrap built‑in):

```bash
pip install ttkbootstrap-icons
```

Optional providers (install what you need):

```bash
pip install ttkbootstrap-icons-fa       # Font Awesome (Free)
pip install ttkbootstrap-icons-mat      # Material Design Icons (MDI)
pip install ttkbootstrap-icons-ion      # Ionicons v2 (font)
pip install ttkbootstrap-icons-remix    # Remix Icon
pip install ttkbootstrap-icons-fluent   # Fluent System Icons
pip install ttkbootstrap-icons-simple   # Simple Icons (community font)
pip install ttkbootstrap-icons-weather  # Weather Icons
pip install ttkbootstrap-icons-lucide   # Lucide Icons
pip install ttkbootstrap-icons-gmi      # Google Material Icons
```

## Quick Usage

Bootstrap (built‑in):

```python
import tkinter as tk
from ttkbootstrap_icons import BootstrapIcon

root = tk.Tk()
icon = BootstrapIcon("house", size=24, color="#0d6efd")
tk.Button(root, image=icon.image, text="Home", compound="left").pack()
root.mainloop()
```

Providers (example):

```python
from ttkbootstrap_icons_fa import FAIcon
btn = tk.Button(root, image=FAIcon("house", 24, "#0d6efd", style="solid").image)
```

## Previewer

Browse installed icon sets with search, styles, and size/color controls:

```bash
ttkbootstrap-icons
```

## Links

- Full documentation and providers: root README
- Project: https://github.com/israel-dryer/ttkbootstrap-icons
- ttkbootstrap: https://ttkbootstrap.readthedocs.io/
