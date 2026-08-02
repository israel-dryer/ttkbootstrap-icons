# ttkbootstrap-icons-gmi

> ### This package has moved
>
> Google Material Icons now ship as an extra of **[tkinter-icons](https://pypi.org/project/tkinter-icons/)**:
>
> ```bash
> pip install "tkinter-icons[google-material]"
> ```
>
> ```python
> from tkinter_icons import GoogleMaterialIcon
> ```
>
> **[Google Material Icons pack documentation](https://tkinter-icons.readthedocs.io/en/latest/packs/google-material.html)**

`ttkbootstrap-icons` was renamed to `tkinter-icons` in 5.0.0. The old name promised a relationship with [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) that no longer holds — Bootstrap icons are built into ttkbootstrap itself now — and the sixteen icon sets moved from separate distributions you install by name to extras of one library.

## What changes for you

| | Before | Now |
|---|---|---|
| Install | `pip install ttkbootstrap-icons-gmi` | `pip install "tkinter-icons[google-material]"` |
| Import | `from ttkbootstrap_icons_gmi import GMatIcon` | `from tkinter_icons import GoogleMaterialIcon` |

**The class is the same.** `GMatIcon` is still exported from `tkinter_icons` (alongside the spelled-out `GoogleMaterialIcon`), so the only edit is the import line. Everything else — `(name, size, color, style)` — is unchanged.

The replacement pack tracks Google Material Icons v0.14.15 and carries 8,936 names across the `baseline`, `outlined`, `round` and `sharp` styles.

Not ready to move? Your existing code keeps working: `ttkbootstrap-icons` 5.0.0 is a forwarding shim that re-exports the old import root. See the [migration notes](https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html).

## About this release

**1.0.2 is the final release of `ttkbootstrap-icons-gmi`.** It ships the same font and the same glyph data as 1.0.1, and draws the same icons. Three things changed:

- this page, which pointed at a layout that no longer exists
- the base pin, now `ttkbootstrap-icons>=3.0.0,<5`, so installing this package keeps resolving the pre-5.0 base it was built against rather than the 5.0 forwarding shim
- importing it now emits a `FutureWarning` naming the replacement

Nothing further will be published under this name.

## Icon set

**Google Material Icons** — [browse the set](https://github.com/marella/material-design-icons) · [upstream license](https://github.com/marella/material-design-icons/blob/main/LICENSE)

The icons are not ours: this package redistributes the upstream font under that project's own license. MIT for the wrapper itself. The upstream license text is bundled in the installed package.

## Links

- [Google Material Icons in the new documentation](https://tkinter-icons.readthedocs.io/en/latest/packs/google-material.html)
- [All sixteen icon packs](https://tkinter-icons.readthedocs.io/en/latest/packs.html)
- [Migrating from ttkbootstrap-icons](https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html)
- [Repository](https://github.com/israel-dryer/tkinter-icons)
