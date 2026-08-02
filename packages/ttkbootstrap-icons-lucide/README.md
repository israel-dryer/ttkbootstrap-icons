# ttkbootstrap-icons-lucide

> ### This package has moved
>
> Lucide Icons now ship as an extra of **[tkinter-icons](https://pypi.org/project/tkinter-icons/)**:
>
> ```bash
> pip install "tkinter-icons[lucide]"
> ```
>
> ```python
> from tkinter_icons import LucideIcon
> ```
>
> **[Lucide Icons pack documentation](https://tkinter-icons.readthedocs.io/en/latest/packs/lucide.html)**

`ttkbootstrap-icons` was renamed to `tkinter-icons` in 5.0.0. The old name promised a relationship with [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) that no longer holds — Bootstrap icons are built into ttkbootstrap itself now — and the sixteen icon sets moved from separate distributions you install by name to extras of one library.

## What changes for you

| | Before | Now |
|---|---|---|
| Install | `pip install ttkbootstrap-icons-lucide` | `pip install "tkinter-icons[lucide]"` |
| Import | `from ttkbootstrap_icons_lucide import LucideIcon` | `from tkinter_icons import LucideIcon` |

**The class is the same.** `LucideIcon` is still exported from `tkinter_icons`, so the only edit is the import line. Everything else — `(name, size, color)` — is unchanged.

The replacement pack tracks Lucide Icons v0.511.0 and carries 1,601 names.

Not ready to move? Your existing code keeps working: `ttkbootstrap-icons` 5.0.0 is a forwarding shim that re-exports the old import root. See the [migration notes](https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html).

## About this release

**1.0.1 is the final release of `ttkbootstrap-icons-lucide`.** It ships the same font and the same glyph data as 1.0.0, and draws the same icons. Three things changed:

- this page, which pointed at a layout that no longer exists
- the base pin, now `ttkbootstrap-icons>=3.0.0,<5`, so installing this package keeps resolving the pre-5.0 base it was built against rather than the 5.0 forwarding shim
- importing it now emits a `FutureWarning` naming the replacement

Nothing further will be published under this name.

## Icon set

**Lucide Icons** — [browse the set](http://lucide.dev/icons/) · [upstream license](https://lucide.dev/license)

The icons are not ours: this package redistributes the upstream font under that project's own license. MIT for the wrapper itself. The upstream license text is bundled in the installed package.

## Links

- [Lucide Icons in the new documentation](https://tkinter-icons.readthedocs.io/en/latest/packs/lucide.html)
- [All sixteen icon packs](https://tkinter-icons.readthedocs.io/en/latest/packs.html)
- [Migrating from ttkbootstrap-icons](https://tkinter-icons.readthedocs.io/en/latest/getting-started/migrating.html)
- [Repository](https://github.com/israel-dryer/tkinter-icons)
