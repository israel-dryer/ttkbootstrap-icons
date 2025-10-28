# ttkbootstrap-icons

Font-based icons for Tkinter/ttkbootstrap with a built-in Bootstrap set and installable providers: Font Awesome,
Material, Ionicons, Remix, Fluent, Simple, Weather, Lucide, Devicon.

## Features

- Built-in set: Bootstrap Icons
- Pluggable providers: Font Awesome, Material, Ionicons, Remix, Fluent, Simple, Weather, Lucide, Devicon
- Style variants where available (e.g., Font Awesome solid/regular/brands, etc...)
- Previewer app: search, style selector, size/color controls, click-to-copy; auto-discovers installed providers
- Cross‑platform; includes PyInstaller hook for bundling assets

## Installation

```bash
pip install ttkbootstrap-icons
```

Optional providers (install any you want):

```bash
pip install ttkbootstrap-icons-fa       # Font Awesome (Free)
pip install ttkbootstrap-icons-fluent   # Fluent System Icons
pip install ttkbootstrap-icons-gmi      # Google Material Icons (baseline/outlined/round/sharp/twotone)
pip install ttkbootstrap-icons-ion      # Ionicons v2 (font)
pip install ttkbootstrap-icons-lucide   # Lucide Icons
pip install ttkbootstrap-icons-mat      # Material Design Icons (MDI)
pip install ttkbootstrap-icons-remix    # Remix Icon
pip install ttkbootstrap-icons-simple   # Simple Icons (community font)
pip install ttkbootstrap-icons-weather  # Weather Icons
pip install ttkbootstrap-icons-devicon  # Devicon
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

### Provider Icons (examples)

```python
import tkinter as tk
from ttkbootstrap_icons_fa import FAIcon            # Font Awesome
from ttkbootstrap_icons_lucide import LucideIcon    # Lucide
from ttkbootstrap_icons_devicon import DevIcon      # Devicon

root = tk.Tk()

fa = FAIcon("house", size=24, color="#0d6efd", style="solid")
luc = LucideIcon("home", size=24, color="#dc3545")
dev = DevIcon("python-plain", size=24, color="#3776AB")

tk.Button(root, image=fa.image, text="FA House", compound="left").pack()
tk.Button(root, image=luc.image, text="Lucide Home", compound="left").pack()
tk.Button(root, image=dev.image, text="Devicon Python", compound="left").pack()

root.mainloop()
```

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

## Icon Previewer

Browse installed icon sets with search, styles, size and color controls. The previewer auto‑discovers any provider packages you have installed.

### Using the CLI Command

After installing the package:

```bash
ttkbootstrap-icons
```

**Features:**

- Shows all installed providers (Bootstrap built‑in; others optional)
- Style selector for sets that provide variants (e.g., FA, Fluent, Material Icons)
- Real‑time search filtering
- Adjustable icon size (16–128 px)
- Color customization with presets
- Virtual scrolling for smooth performance
- Fixed window for consistent layout

**Controls:**

- Icon Set: Choose among installed icon sets
- Style: Select a style variant when available
- Search: Filter icons by name (case‑insensitive)
- Size: Set preview size
- Color: Enter any Tkinter color (hex, names)
- Presets: Quick color buttons
- Click to Copy: Click any icon to copy its name

![Icon Previewer](https://raw.githubusercontent.com/israel-dryer/ttkbootstrap-icons/main/examples/previewer-2.png)

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

## License

MIT License - see LICENSE file for details

## Author

Israel Dryer (israel.dryer@gmail.com)

## Links

- [GitHub Repository](https://github.com/israel-dryer/ttkbootstrap-icons)
- [Third-Party Notices](./THIRD-PARTY-NOTICES.md)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)
- [Material Design Icons (MDI)](https://materialdesignicons.com/)
- [Ionicons](https://ionic.io/ionicons)
- [Remix Icon](https://remixicon.com/)
- [Fluent System Icons](https://github.com/microsoft/fluentui-system-icons)
- [Simple Icons](https://simpleicons.org/)
- [Weather Icons](https://erikflowers.github.io/weather-icons/)
- [Lucide Icons](https://lucide.dev/)
- [Material Icons (Google)](https://fonts.google.com/icons)
- [Devicon](https://devicon.dev)
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/)
