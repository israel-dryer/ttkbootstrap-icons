# ttkbootstrap-icons-bs

> ### This package has moved
>
> Bootstrap Icons now ship as an extra of **[tkinter-icons](https://pypi.org/project/tkinter-icons/)**:
>
> ```bash
> pip install "tkinter-icons[bootstrap]"
> ```
>
> ```python
> from tkinter_icons import BootstrapIcon
> ```
>
> **[Bootstrap Icons pack documentation](https://tkinter-icons.readthedocs.io/en/latest/packs/bootstrap.html)**

`ttkbootstrap-icons` was renamed to `tkinter-icons` in 5.0.0. The old name promised a relationship with [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) that no longer holds — Bootstrap icons are built into ttkbootstrap itself now — and the sixteen icon sets moved from separate distributions you install by name to extras of one library.

## What changes for you

| | Before | Now |
|---|---|---|
| Install | `pip install ttkbootstrap-icons-bs` | `pip install "tkinter-icons[bootstrap]"` |
| Import | `from ttkbootstrap_icons_bs import BootstrapIcon` | `from tkinter_icons import BootstrapIcon` |

**The class is the same.** `BootstrapIcon` is still exported from `tkinter_icons`, so the only edit is the import line. Everything else — `(name, size, color, style)` — is unchanged.

The replacement pack tracks Bootstrap Icons v1.13.1 and carries 2,078 names across the `fill` and `outline` styles.

Not ready to move? Your existing code keeps working: `ttkbootstrap-icons` 5.0.0 is a forwarding shim that re-exports the old import root. See the [migration notes](https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html).

## About this release

**1.0.1 is the final release of `ttkbootstrap-icons-bs`.** It ships the same font and the same glyph data as 1.0.0, and draws the same icons. Three things changed:

- this page, which pointed at a layout that no longer exists
- the base pin, now `ttkbootstrap-icons>=4.0.0,<5`, so installing this package keeps resolving the pre-5.0 base it was built against rather than the 5.0 forwarding shim
- importing it now emits a `FutureWarning` naming the replacement

Nothing further will be published under this name.

## Icon set

**Bootstrap Icons** — [browse the set](https://icons.getbootstrap.com/) · [upstream license](https://github.com/twbs/icons/blob/main/LICENSE)

The icons are not ours: this package redistributes the upstream font under that project's own license. MIT for the wrapper itself. The upstream license text is not bundled in this release; follow the link above. The replacement pack ships it.

## Links

- [Bootstrap Icons in the new documentation](https://tkinter-icons.readthedocs.io/en/latest/packs/bootstrap.html)
- [All sixteen icon packs](https://tkinter-icons.readthedocs.io/en/latest/packs.html)
- [Migrating from ttkbootstrap-icons](https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html)
- [Repository](https://github.com/israel-dryer/tkinter-icons)
