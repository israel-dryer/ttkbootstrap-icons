# ttkbootstrap-icons Monorepo

[![PyPI](https://img.shields.io/pypi/v/ttkbootstrap-icons.svg)](https://pypi.org/project/ttkbootstrap-icons/)
[![Python Versions](https://img.shields.io/pypi/pyversions/ttkbootstrap-icons.svg)](https://pypi.org/project/ttkbootstrap-icons/)
[![Downloads](https://static.pepy.tech/badge/ttkbootstrap-icons)](https://pepy.tech/project/ttkbootstrap-icons)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Font-based icons for Tkinter/ttkbootstrap with a built-in Bootstrap set and installable provider packages: Font Awesome,
Material, Ionicons, Remix, Fluent, Simple, Weather, Lucide, Devicon, Eva, Typicons & more. Includes a fast Icon Browser
for search, style selection, color/size controls, and click-to-copy names.

Docs: https://israel-dryer.github.io/ttkbootstrap-icons/

---

## Install (Core)

```bash
pip install ttkbootstrap-icons
```

Providers are install-what-you-need (examples):

```bash
pip install ttkbootstrap-icons-fa ttkbootstrap-icons-gmi ttkbootstrap-icons-remix
```

See the documentation for the full provider list and usage examples.

---

## Quick Start

```python
import tkinter as tk
from ttkbootstrap_icons import BootstrapIcon

root = tk.Tk()
icon = BootstrapIcon("house", size=24, color="#0d6efd", style="fill")
tk.Label(root, image=icon.image, text=" Home", compound="left").pack(padx=10, pady=10)
root.mainloop()
```

Launch the Icon Browser to explore installed icon sets:

```bash
ttkbootstrap-icons
# or
python -m ttkbootstrap_icons.browser
```

![Icon Browser](/packages/ttkbootstrap-icons/browser.png)

---

## Packages

This is a multi-package (monorepo) workspace.

| Package                                                                                                       | PyPI                                                           | Downloads                                                                                                                  | Description                                                |
|:--------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------|
| [ttkbootstrap-icons](https://israel-dryer.github.io/ttkbootstrap-icons/)                                      | [PyPI](https://pypi.org/project/ttkbootstrap-icons/)           | [![](https://static.pepy.tech/badge/ttkbootstrap-icons)](https://pepy.tech/project/ttkbootstrap-icons)                     | Core library, built-in Bootstrap provider and Icon Browser |
| [ttkbootstrap-icons-fa](https://israel-dryer.github.io/ttkbootstrap-icons/providers/font-awesome-6-free/)     | [PyPI](https://pypi.org/project/ttkbootstrap-icons-fa/)        | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-fa)](https://pepy.tech/project/ttkbootstrap-icons-fa)               | Font Awesome (Free)                                        |
| [ttkbootstrap-icons-gmi](https://israel-dryer.github.io/ttkbootstrap-icons/providers/google-material-icons/)  | [PyPI](https://pypi.org/project/ttkbootstrap-icons-gmi/)       | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-gmi)](https://pepy.tech/project/ttkbootstrap-icons-gmi)             | Google Material Icons                                      |
| [ttkbootstrap-icons-ion](https://israel-dryer.github.io/ttkbootstrap-icons/providers/ion/)                    | [PyPI](https://pypi.org/project/ttkbootstrap-icons-ion/)       | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-ion)](https://pepy.tech/project/ttkbootstrap-icons-ion)             | Ionicons v2 (font)                                         |
| [ttkbootstrap-icons-remix](https://israel-dryer.github.io/ttkbootstrap-icons/providers/remix/)                | [PyPI](https://pypi.org/project/ttkbootstrap-icons-remix/)     | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-remix)](https://pepy.tech/project/ttkbootstrap-icons-remix)         | Remix Icon                                                 |
| [ttkbootstrap-icons-fluent](https://israel-dryer.github.io/ttkbootstrap-icons/providers/fluent-system-icons/) | [PyPI](https://pypi.org/project/ttkbootstrap-icons-fluent/)    | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-fluent)](https://pepy.tech/project/ttkbootstrap-icons-fluent)       | Fluent System Icons                                        |
| [ttkbootstrap-icons-simple](https://israel-dryer.github.io/ttkbootstrap-icons/providers/simple/)              | [PyPI](https://pypi.org/project/ttkbootstrap-icons-simple/)    | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-simple)](https://pepy.tech/project/ttkbootstrap-icons-simple)       | Simple Icons (brand logos)                                 |
| [ttkbootstrap-icons-weather](https://israel-dryer.github.io/ttkbootstrap-icons/providers/weather/)            | [PyPI](https://pypi.org/project/ttkbootstrap-icons-weather/)   | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-weather)](https://pepy.tech/project/ttkbootstrap-icons-weather)     | Weather Icons                                              |
| [ttkbootstrap-icons-lucide](https://israel-dryer.github.io/ttkbootstrap-icons/providers/lucide/)              | [PyPI](https://pypi.org/project/ttkbootstrap-icons-lucide/)    | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-lucide)](https://pepy.tech/project/ttkbootstrap-icons-lucide)       | Lucide Icons                                               |
| [ttkbootstrap-icons-mat](https://israel-dryer.github.io/ttkbootstrap-icons/providers/material-design-icons/)  | [PyPI](https://pypi.org/project/ttkbootstrap-icons-mat/)       | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-mat)](https://pepy.tech/project/ttkbootstrap-icons-mat)             | Material Design Icons (MDI)                                |
| [ttkbootstrap-icons-devicon](https://israel-dryer.github.io/ttkbootstrap-icons/providers/devicon/)            | [PyPI](https://pypi.org/project/ttkbootstrap-icons-devicon/)   | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-devicon)](https://pepy.tech/project/ttkbootstrap-icons-devicon)     | Devicon                                                    |
| [ttkbootstrap-icons-eva](https://israel-dryer.github.io/ttkbootstrap-icons/providers/eva/)                    | [PyPI](https://pypi.org/project/ttkbootstrap-icons-eva/)       | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-eva)](https://pepy.tech/project/ttkbootstrap-icons-eva)             | Eva Icons                                                  |
| [ttkbootstrap-icons-typicons](https://israel-dryer.github.io/ttkbootstrap-icons/providers/typicons/)          | [PyPI](https://pypi.org/project/ttkbootstrap-icons-typicons/)  | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-typicons)](https://pepy.tech/project/ttkbootstrap-icons-typicons)   | Typicons                                                   |
| [ttkbootstrap-icons-meteocons](https://israel-dryer.github.io/ttkbootstrap-icons/providers/meteocons/)        | [PyPI](https://pypi.org/project/ttkbootstrap-icons-meteocons/) | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-meteocons)](https://pepy.tech/project/ttkbootstrap-icons-meteocons) | Meteocons                                                  |
| [ttkbootstrap-icons-rpga](https://israel-dryer.github.io/ttkbootstrap-icons/providers/rgpa/)                  | [PyPI](https://pypi.org/project/ttkbootstrap-icons-rpga/)      | [![](https://static.pepy.tech/badge/ttkbootstrap-icons-rpga)](https://pepy.tech/project/ttkbootstrap-icons-rpga)           | RPG Awesome                                                |

---

## Contributors

Contributions are welcome! See the contributing guide for provider templates, naming conventions, and docs integration:

- https://israel-dryer.github.io/ttkbootstrap-icons/contributing/

You can also open an issue or pull request in this repository.

## License & Notices

Refer to the documentation for the project license and all third‑party notices:

https://israel-dryer.github.io/ttkbootstrap-icons/license/

For convenience, the root LICENSE file is also included in this repository.


