# tkinter-icons

[![PyPI](https://img.shields.io/pypi/v/tkinter-icons.svg)](https://pypi.org/project/tkinter-icons/)
[![Python Versions](https://img.shields.io/pypi/pyversions/tkinter-icons.svg)](https://pypi.org/project/tkinter-icons/)
[![Downloads](https://static.pepy.tech/badge/tkinter-icons)](https://pepy.tech/project/tkinter-icons)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Font-based icons for Tkinter/ttkbootstrap with installable provider packages: Bootstrap Icons, Font Awesome,
Material, Ionicons, Remix, Fluent, Simple, Weather, Lucide, Devicon, Eva, Typicons & more. Includes a fast Icon Browser
for search, style selection, color/size controls, and click-to-copy names.

Docs: https://israel-dryer.github.io/tkinter-icons/

---

## Install

Install the base package and at least one icon provider:

```bash
pip install tkinter-icons tkinter-icons-bs
```

Additional providers (install what you need):

```bash
pip install tkinter-icons-fa tkinter-icons-gmi tkinter-icons-remix
```

See the documentation for the full provider list and usage examples.

---

## Quick Start

```python
import tkinter as tk
from tkinter_icons_bs import BootstrapIcon

root = tk.Tk()
icon = BootstrapIcon("house", size=24, color="#0d6efd", style="fill")
tk.Label(root, image=icon.image, text=" Home", compound="left").pack(padx=10, pady=10)
root.mainloop()
```

Launch the Icon Browser to explore installed icon sets:

```bash
tkinter-icons
# or
python -m tkinter_icons.browser
```

![Icon Browser](/packages/tkinter-icons/browser.png)

---

## Stateful Icons (v3.1.0+)

Icons can automatically change appearance based on widget states (hover, pressed, disabled, selected):

```python
import ttkbootstrap as tb
from tkinter_icons_bs import BootstrapIcon

app = tb.Window()
icon = BootstrapIcon("mic-mute-fill", size=64)
toggle = tb.Checkbutton(app, compound="image", bootstyle="toolbutton")
toggle.pack(padx=20, pady=20)

# Icon automatically switches to mic-fill when selected
icon.map(toggle, statespec=[("selected", {"name": "mic-fill"})])

app.mainloop()
```

See the [Stateful Icons documentation](https://israel-dryer.github.io/tkinter-icons/stateful-icons/) for automatic color mapping, custom state specifications, and advanced examples.

---

## Packages

This is a multi-package (monorepo) workspace that includes all of the extension icon packages within the
`tkinter-icons` family.

| Package                                                                                                       | PyPI                                                           | Downloads                                                                                                                  | Description                                                |
|:--------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------|
| [tkinter-icons](https://israel-dryer.github.io/tkinter-icons/)                                      | [PyPI](https://pypi.org/project/tkinter-icons/)           | [![](https://static.pepy.tech/badge/tkinter-icons)](https://pepy.tech/project/tkinter-icons)                     | Core library with provider framework and Icon Browser      |
| [tkinter-icons-bs](https://israel-dryer.github.io/tkinter-icons/providers/bootstrap/)               | [PyPI](https://pypi.org/project/tkinter-icons-bs/)        | [![](https://static.pepy.tech/badge/tkinter-icons-bs)](https://pepy.tech/project/tkinter-icons-bs)               | Bootstrap Icons                                            |
| [tkinter-icons-fa](https://israel-dryer.github.io/tkinter-icons/providers/font-awesome-6-free/)     | [PyPI](https://pypi.org/project/tkinter-icons-fa/)        | [![](https://static.pepy.tech/badge/tkinter-icons-fa)](https://pepy.tech/project/tkinter-icons-fa)               | Font Awesome (Free)                                        |
| [tkinter-icons-gmi](https://israel-dryer.github.io/tkinter-icons/providers/google-material-icons/)  | [PyPI](https://pypi.org/project/tkinter-icons-gmi/)       | [![](https://static.pepy.tech/badge/tkinter-icons-gmi)](https://pepy.tech/project/tkinter-icons-gmi)             | Google Material Icons                                      |
| [tkinter-icons-ion](https://israel-dryer.github.io/tkinter-icons/providers/ion/)                    | [PyPI](https://pypi.org/project/tkinter-icons-ion/)       | [![](https://static.pepy.tech/badge/tkinter-icons-ion)](https://pepy.tech/project/tkinter-icons-ion)             | Ionicons v2 (font)                                         |
| [tkinter-icons-remix](https://israel-dryer.github.io/tkinter-icons/providers/remix/)                | [PyPI](https://pypi.org/project/tkinter-icons-remix/)     | [![](https://static.pepy.tech/badge/tkinter-icons-remix)](https://pepy.tech/project/tkinter-icons-remix)         | Remix Icon                                                 |
| [tkinter-icons-fluent](https://israel-dryer.github.io/tkinter-icons/providers/fluent-system-icons/) | [PyPI](https://pypi.org/project/tkinter-icons-fluent/)    | [![](https://static.pepy.tech/badge/tkinter-icons-fluent)](https://pepy.tech/project/tkinter-icons-fluent)       | Fluent System Icons                                        |
| [tkinter-icons-fluent-reg](https://israel-dryer.github.io/tkinter-icons/providers/fluent-system-icons-regular/) | [PyPI](https://pypi.org/project/tkinter-icons-fluent-reg/) | [![](https://static.pepy.tech/badge/tkinter-icons-fluent-reg)](https://pepy.tech/project/tkinter-icons-fluent-reg) | Fluent System Icons (Regular only)                        |
| [tkinter-icons-simple](https://israel-dryer.github.io/tkinter-icons/providers/simple/)              | [PyPI](https://pypi.org/project/tkinter-icons-simple/)    | [![](https://static.pepy.tech/badge/tkinter-icons-simple)](https://pepy.tech/project/tkinter-icons-simple)       | Simple Icons (brand logos)                                 |
| [tkinter-icons-weather](https://israel-dryer.github.io/tkinter-icons/providers/weather/)            | [PyPI](https://pypi.org/project/tkinter-icons-weather/)   | [![](https://static.pepy.tech/badge/tkinter-icons-weather)](https://pepy.tech/project/tkinter-icons-weather)     | Weather Icons                                              |
| [tkinter-icons-lucide](https://israel-dryer.github.io/tkinter-icons/providers/lucide/)              | [PyPI](https://pypi.org/project/tkinter-icons-lucide/)    | [![](https://static.pepy.tech/badge/tkinter-icons-lucide)](https://pepy.tech/project/tkinter-icons-lucide)       | Lucide Icons                                               |
| [tkinter-icons-mat](https://israel-dryer.github.io/tkinter-icons/providers/material-design-icons/)  | [PyPI](https://pypi.org/project/tkinter-icons-mat/)       | [![](https://static.pepy.tech/badge/tkinter-icons-mat)](https://pepy.tech/project/tkinter-icons-mat)             | Material Design Icons (MDI)                                |
| [tkinter-icons-devicon](https://israel-dryer.github.io/tkinter-icons/providers/devicon/)            | [PyPI](https://pypi.org/project/tkinter-icons-devicon/)   | [![](https://static.pepy.tech/badge/tkinter-icons-devicon)](https://pepy.tech/project/tkinter-icons-devicon)     | Devicon                                                    |
| [tkinter-icons-eva](https://israel-dryer.github.io/tkinter-icons/providers/eva/)                    | [PyPI](https://pypi.org/project/tkinter-icons-eva/)       | [![](https://static.pepy.tech/badge/tkinter-icons-eva)](https://pepy.tech/project/tkinter-icons-eva)             | Eva Icons                                                  |
| [tkinter-icons-typicons](https://israel-dryer.github.io/tkinter-icons/providers/typicons/)          | [PyPI](https://pypi.org/project/tkinter-icons-typicons/)  | [![](https://static.pepy.tech/badge/tkinter-icons-typicons)](https://pepy.tech/project/tkinter-icons-typicons)   | Typicons                                                   |
| [tkinter-icons-meteocons](https://israel-dryer.github.io/tkinter-icons/providers/meteocons/)        | [PyPI](https://pypi.org/project/tkinter-icons-meteocons/) | [![](https://static.pepy.tech/badge/tkinter-icons-meteocons)](https://pepy.tech/project/tkinter-icons-meteocons) | Meteocons                                                  |
| [tkinter-icons-rpga](https://israel-dryer.github.io/tkinter-icons/providers/rgpa/)                  | [PyPI](https://pypi.org/project/tkinter-icons-rpga/)      | [![](https://static.pepy.tech/badge/tkinter-icons-rpga)](https://pepy.tech/project/tkinter-icons-rpga)           | RPG Awesome                                                |

---

## Contributors

Contributions are welcome! See the contributing guide for provider templates, naming conventions, and docs integration:

- https://israel-dryer.github.io/tkinter-icons/contributing/

You can also open an issue or pull request in this repository.

## License & Notices

Refer to the documentation for the project license and all third‑party notices:

https://israel-dryer.github.io/tkinter-icons/license/

For convenience, the root LICENSE file is also included in this repository.


