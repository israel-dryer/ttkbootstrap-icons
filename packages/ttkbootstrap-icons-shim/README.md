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
pip install "tkinter-icons[material]"
```

Icon packs are now extras, one per set, and there is no `[all]` — name the ones
you use: `pip install "tkinter-icons[bootstrap,material]"`.

Then change your imports, which now all come from one root:

```python
from ttkbootstrap_icons_mat import MatIcon    # old
from tkinter_icons import MaterialIcon        # new
```

See the [documentation](https://tkinter-icons.readthedocs.io/en/latest/) for the
full list of packs.
