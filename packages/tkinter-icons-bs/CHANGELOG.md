# Changelog

All notable changes to `tkinter-icons-bs` are documented in this file.
The base package keeps its own changelog at the root of the repository.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This pack was published as `ttkbootstrap-icons-bs` through 1.0.x and renamed
to `tkinter-icons-bs` in 1.1.0. Entries before 1.1.0 were reconstructed from
git history after the fact and are summaries rather than contemporaneous notes.

<!-- release-notes-start -->

## [1.1.0] — measured ink metrics, and the tkinter-icons rename

Requires `tkinter-icons>=5.0.0`. Install it as an extra rather than by name:

```bash
pip install "tkinter-icons[bootstrap]"
```

### Added

- **`metrics.json`, the measured ink bounds for every glyph in this pack.** The
  5.0.0 renderer centers on true ink instead of on Pillow's `font.getbbox()`,
  which under-reports it on icon fonts. Without this file the pack still
  renders, by falling back to `getbbox`; with it, full-bleed icons keep their
  padding and everything else sits centered. Regenerate with
  `python -m tkinter_icons.tools.generate_metrics bootstrap` whenever the font
  or glyph map changes. (#67)

- **Bootstrap Icons' MIT license, at `assets/LICENSES/MIT.txt`.** This pack redistributes an upstream icon font and did not carry its license text, which every other pack does. The file is upstream's own, copied unedited from [twbs/icons](https://github.com/twbs/icons/blob/main/LICENSE), and it ships in the wheel.

- **The icon class takes `options`.** `RenderOptions` carries every drawing knob — padding, oversampling, sharpening, even-snapping — and was reachable only through `Icon.render_pil` or the base `Icon`, not through the class you actually construct. `BootstrapIcon("name", size=32, options=RenderOptions(pad_factor=0.0))` now works. Keyword-only, so it cannot be confused with `style`.

- **`render_pil` works on this class without a warm-up.** It read an icon set shared by every subclass, so `BootstrapIcon.render_pil(...)` drew this pack's glyphs only if something had already constructed one of its icons — and raised in a fresh process. The class names its own provider now, and resolves friendly names the way the constructor does.

### Changed

- **Renamed from `ttkbootstrap-icons-bs`.** The old distribution is frozen at
  1.0.x and keeps working against a 4.x base package; it will not be updated.
  (#75)

- **The entry point moved to the `tkinter_icons.providers` group.** The base
  package scans the old group as well, so a mixed set of old and new packs stays
  discoverable. (#75)

## [1.0.0] — extracted from the base package

### Added

- **Bootstrap Icons as their own distribution.** Base package 4.0.0 removed the
  built-in icon set, so what used to ship inside `ttkbootstrap-icons` lives here.
  An install that relied on Bootstrap being built in needs this pack added.
