# Fluent System Icons (Regular)

Fluent System Icons Regular is a lightweight provider package that includes only the Regular style from Microsoft's Fluent System Icons.

If you need multiple styles (Regular, Filled, Light), use the full [ttkbootstrap-icons-fluent](fluent-system-icons.md) package instead.

---

## Install

```bash
pip install ttkbootstrap-icons-fluent-reg
```

---

## Quick start

```python
import tkinter as tk
from ttkbootstrap_icons_fluent_reg import FluentRegularIcon

root = tk.Tk()

icon = FluentRegularIcon("settings-16", size=24, color="#333")

tk.Label(root, text="Settings", image=icon.image, compound="left").pack()

root.mainloop()
```

---

## Features

- **Lightweight**: Only includes the Regular style (smaller package size)
- **Simple API**: No style parameter needed - always uses Regular
- **Full icon set**: Includes all Regular icons from Fluent System Icons v1.1.261

---

## When to use this package

**Use `ttkbootstrap-icons-fluent-reg` when:**
- You only need the Regular style
- You want to minimize package size
- You want a simpler API without style selection

**Use `ttkbootstrap-icons-fluent` when:**
- You need multiple styles (Regular, Filled, Light)
- You want to switch between styles at runtime

---

## License and Attribution

- Upstream: Fluent System Icons — https://github.com/microsoft/fluentui-system-icons
- Wrapper license: MIT (c) Israel Dryer