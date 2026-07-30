# Bootstrap Icons

Bootstrap Icons is a separate provider package for tkinter-icons.

---

## Install

```bash
pip install tkinter-icons-bs
```

---

## Quick start

```python
import tkinter as tk
from tkinter_icons import BootstrapIcon

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
tkinter-icons
```

Use "Copy Name" in the browser to copy the icon name and style directly for use in your code.

![Icon Browser](assets/bootstrap/browser.png)

---

## License and Attribution

- Upstream: Bootstrap Icons — https://icons.getbootstrap.com/
- Wrapper license: MIT (c) Israel Dryer
