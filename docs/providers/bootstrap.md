# Bootstrap Icons (built-in)

The base `ttkbootstrap-icons` package includes the Bootstrap Icons provider out of the box. No extra install is required beyond the base package.

---

## Install

```bash
pip install ttkbootstrap-icons
```

---

## Quick start

```python
import tkinter as tk
from ttkbootstrap_icons import BootstrapIcon

root = tk.Tk()

outline = BootstrapIcon("house", size=24, color="#333", style="outline")
filled = BootstrapIcon("house", size=24, color="#333", style="fill")

tk.Label(root, text="Outline", image=outline.image, compound="left").pack()
tk.Label(root, text="Fill", image=filled.image, compound="left").pack()

root.mainloop()
```

---

## Styles

| Variant  | Description            |
|:---------|:-----------------------|
| `outline`| Outline stroke variant |
| `fill`   | Filled variant         |

---

## Icon Browser

Browse available icons with the built-in browser. From your terminal run:

```bash
ttkbootstrap-icons
```

Use "Copy Name" in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](assets/bootstrap/browser.png)

---

## License and Attribution

- Upstream: Bootstrap Icons — https://icons.getbootstrap.com/
- Wrapper license: MIT (c) Israel Dryer
