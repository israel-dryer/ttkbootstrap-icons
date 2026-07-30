# tkinter-icons-bs

Bootstrap Icons provider for tkinter-icons.

## Installation

```bash
pip install tkinter-icons-bs
```

## Usage

```python
from tkinter_icons_bs import BootstrapIcon

# Create an icon
icon = BootstrapIcon("house", size=24, color="black", style="outline")

# Use in a tkinter widget
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
label = ttk.Label(root, text="Home", image=icon.image, compound="left")
label.pack()
root.mainloop()
```

## Styles

Bootstrap Icons supports two styles:
- `outline` (default)
- `fill`

You can specify the style either as a parameter or as part of the icon name:

```python
# Using style parameter
icon1 = BootstrapIcon("house", style="fill")

# Using style in name
icon2 = BootstrapIcon("house-fill")
```

## License

MIT License

Bootstrap Icons are licensed under the MIT License.
See https://github.com/twbs/icons/blob/main/LICENSE
