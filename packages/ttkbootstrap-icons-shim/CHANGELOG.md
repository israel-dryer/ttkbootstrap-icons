# Changelog

All notable changes to `ttkbootstrap-icons` are documented in this file.

Versions through 4.0.0 were the real library, and their history lives in the
[root changelog](https://github.com/israel-dryer/tkinter-icons/blob/main/CHANGELOG.md)
of what is now `tkinter-icons`. From 5.0.0 this distribution is a forwarding
shim and nothing else.

<!-- release-notes-start -->

## [5.0.0] — forwards to tkinter-icons

`ttkbootstrap-icons` was renamed to **`tkinter-icons`**. Bootstrap icons are
built directly into ttkbootstrap and bootstack now, so the old name described
the wrong thing.

This release exists so that installs of the old name keep working. It is
published **once** and will not be updated again — it depends on
`tkinter-icons>=5.0.0` with no upper bound, so it forwards to every future
version on its own.

Move to the new name when convenient:

```bash
pip uninstall ttkbootstrap-icons
pip install "tkinter-icons[bootstrap]"
```

```python
from tkinter_icons import Icon          # was: from ttkbootstrap_icons import Icon
```

### Changed

- **The package is now a shim over `tkinter-icons`.** It re-exports the public
  API and aliases the submodules into `sys.modules`, so
  `from ttkbootstrap_icons.icon import Icon` resolves as it always did. (#75)

- **Importing it warns once, as a `FutureWarning`.** Not a
  `DeprecationWarning` — Python hides those unless they fire in `__main__`, so
  an app that imports the package from a module would never have seen it. (#75)

### Note

Icon packs published under the old `ttkbootstrap-icons-*` names have **no**
shims. They are frozen at 1.0.x and keep working against a 4.x base package.
To move to 5.0.0, install the packs you use as extras of `tkinter-icons`.