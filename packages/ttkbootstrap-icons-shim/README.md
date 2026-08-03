# ttkbootstrap-icons

**This package has been renamed to [`tkinter-icons`](https://pypi.org/project/tkinter-icons/).**

The old name implied a coupling to ttkbootstrap that was never really true — the
library works with plain tkinter, and Bootstrap icons are now built directly into
ttkbootstrap itself.

This package now contains no code. It depends on `tkinter-icons` and forwards to
it, so existing installs keep working, and it will not receive further updates.

## Switching over

```bash
pip uninstall ttkbootstrap-icons
pip install "tkinter-icons[all]"     # or just the packs you use
```

Then change your imports:

```python
from ttkbootstrap_icons_mat import MatIcon    # old
from tkinter_icons import MaterialIcon        # new
```

Icon packs are now extras, so you install and import one name:

```bash
pip install "tkinter-icons[material]"
```

See the [documentation](https://tkinter-icons.readthedocs.io/en/latest/) for the
full list of packs.
