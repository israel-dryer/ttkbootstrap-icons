# ttkbootstrap-icons-fluent-reg

Fluent System Icons (Regular style only) provider for ttkbootstrap-icons.

This is a lightweight package that includes only the Regular style from Microsoft's Fluent System Icons. If you need multiple styles (Regular, Filled, Light), use the full `ttkbootstrap-icons-fluent` package instead.

## Installation

```bash
pip install ttkbootstrap-icons-fluent-reg
```

## Usage

```python
from ttkbootstrap_icons_fluent_reg import FluentRegularIcon

# Create an icon
icon = FluentRegularIcon("settings-16", size=24, color="black")

# Use in a tkinter widget
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
label = ttk.Label(root, text="Settings", image=icon.image, compound="left")
label.pack()
root.mainloop()
```

## Features

- **Lightweight**: Only includes the Regular style (smaller package size)
- **Simple API**: No style parameter needed - always uses Regular
- **Full icon set**: Includes all Regular icons from Fluent System Icons v1.1.261

## When to use this package

Use `ttkbootstrap-icons-fluent-reg` when:
- You only need the Regular style
- You want to minimize package size
- You want a simpler API without style selection

Use `ttkbootstrap-icons-fluent` when:
- You need multiple styles (Regular, Filled, Light)
- You want to switch between styles at runtime

## License

MIT License

Fluent System Icons are licensed under the MIT License by Microsoft.
See https://github.com/microsoft/fluentui-system-icons/blob/main/LICENSE