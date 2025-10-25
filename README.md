# ttkbootstrap-icons

A Python package for using Bootstrap Icons and Lucide Icons in your tkinter/ttkbootstrap applications.

![Icon Previewer](https://raw.githubusercontent.com/israel-dryer/ttkbootstrap-icons/main/examples/previewer.png)

## Features

- **Two Icon Sets**: Access to both Bootstrap Icons and Lucide Icons
- **Easy to Use**: Simple API for creating icons
- **Customizable**: Adjust icon size and color on the fly
- **Lightweight**: Uses icon fonts for efficient rendering
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

```bash
pip install ttkbootstrap-icons
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

- **Bootstrap Icons**: See the [Bootstrap Icons website](https://icons.getbootstrap.com/) for a full list of available icons
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

The repository includes example applications demonstrating various use cases. These are available in the [examples directory](https://github.com/israel-dryer/ttkbootstrap-icons/tree/main/examples) on GitHub.

### Basic Example

A simple application showing both Bootstrap and Lucide icons in buttons:

```python
import atexit
import tkinter as tk
from tkinter import ttk

from ttkbootstrap_icons import BootstrapIcon, LucideIcon
from ttkbootstrap_icons.icon import Icon


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

The package includes an interactive icon previewer application to browse all available icons.

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
- Browse 2078+ Bootstrap icons or 1601+ Lucide icons
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

This package includes built-in PyInstaller support. The icon assets (fonts and metadata) will be automatically included when you freeze your application.

### Basic Usage

```bash
pip install pyinstaller
pyinstaller --onefile your_app.py
```

### With Hook Directory (Automatic)

The package includes a PyInstaller hook that automatically bundles the required assets. In most cases, PyInstaller will detect and use this hook automatically.

### Manual Hook Configuration (If Needed)

If the automatic detection doesn't work, you can manually specify the hook directory:

```python
# your_app.spec file or command line
pyinstaller --additional-hooks-dir=path/to/site-packages/ttkbootstrap_icons/_pyinstaller your_app.py
```

Or in your `.spec` file:

```python
a = Analysis(
    ['your_app.py'],
    ...
    hookspath=['path/to/site-packages/ttkbootstrap_icons/_pyinstaller'],
    ...
)
```

### Programmatic Hook Discovery

```python
from ttkbootstrap_icons._pyinstaller import get_hook_dirs

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
from ttkbootstrap_icons.icon import Icon

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
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Lucide Icons](https://lucide.dev/)
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/)