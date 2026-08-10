# Changelog

All notable changes to `tkinter-icons-mat` are documented in this file.
The base package keeps its own changelog at the root of the repository.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This pack was published as `ttkbootstrap-icons-mat` through 1.0.x and renamed
to `tkinter-icons-mat` in 1.1.0. Entries before 1.1.0 were reconstructed from
git history after the fact and are summaries rather than contemporaneous notes.

<!-- release-notes-start -->

## [1.1.2] — drops a placeholder name the font never had a glyph for

No font change and no metrics change. Two glyph-map entries are gone, both spellings of one name.

### Changed

- **`blank` and `mdi-blank` are gone.** Upstream's stylesheet declares `mdi-blank` at U+F68C as a deliberately empty placeholder, and the webfont has no such codepoint — so the pack advertised an icon that drew nothing, raised nothing, and warned nothing in either style. Asking for either spelling now raises `ValueError`. Anyone using it as a spacer wants a transparent image rather than an icon; `create_transparent_icon` is that, and it does not depend on a font carrying an empty glyph. (#140)

### Fixed

- **The generator checks the stylesheet's names against the font before writing them.** The glyph map is scraped from upstream's CSS whenever one is available, and a stylesheet is not a font: `mdi-blank` was in the CSS and never in the TTF. Only the font can settle which names are real, so the mapping is now filtered against it and a regeneration cannot reintroduce this. (#140)

## [1.1.1] — an intro in this library's voice

No glyph, font or metrics change: this release exists to correct text that PyPI freezes at release time.

### Changed

- **The README intro and the distribution summary are written from this library's side rather than upstream's.** They now say what the set covers and when to reach for it, instead of repeating the upstream project's own description of the font. (#120)

## [1.1.0] — measured ink metrics, and the tkinter-icons rename

Requires `tkinter-icons>=5.0.0`. Install it as an extra rather than by name:

```bash
pip install "tkinter-icons[material]"
```

### Added

- **`metrics.json`, the measured ink bounds for every glyph in this pack.** The
  5.0.0 renderer centers on true ink instead of on Pillow's `font.getbbox()`,
  which under-reports it on icon fonts. Without this file the pack still
  renders, by falling back to `getbbox`; with it, full-bleed icons keep their
  padding and everything else sits centered. Regenerate with
  `python -m tkinter_icons.tools.generate_metrics mat` whenever the font or
  glyph map changes. (#67)

- **The icon class takes `options`.** `RenderOptions` carries every drawing knob — padding, oversampling, sharpening, even-snapping — and was reachable only through `Icon.render_pil` or the base `Icon`, not through the class you actually construct. `MatIcon("name", size=32, options=RenderOptions(pad_factor=0.0))` now works. Keyword-only, so it cannot be confused with `style`.

- **`render_pil` works on this class without a warm-up.** It read an icon set shared by every subclass, so `MatIcon.render_pil(...)` drew this pack's glyphs only if something had already constructed one of its icons — and raised in a fresh process. The class names its own provider now, and resolves friendly names the way the constructor does.

### Changed

- **Renamed from `ttkbootstrap-icons-mat`.** The old distribution is frozen at
  1.0.x and keeps working against a 4.x base package; it will not be updated.
  (#75)

- **The entry point moved to the `tkinter_icons.providers` group.** The base
  package scans the old group as well, so a mixed set of old and new packs stays
  discoverable. (#75)

### Removed

- **The `tkicons-mat-build` and `tkicons-mat-quick` commands, and the
  `tools` module behind them.** They regenerate this pack's assets from
  upstream sources, so they only work against a source checkout — from an
  installed wheel they did nothing but occupy two names on every user's PATH.
  Nothing imports them at runtime. Maintainers run them from the repository.
  (#79)

## [1.0.0] — one provider API

### Changed

- **Rewritten against the single provider API introduced in base 3.0.0.** Names,
  styles, and display names resolve the same way here as in every other pack,
  whether a style is passed as an argument or carried in the icon name. (#31)

### Added

- **A visual test** covering the pack's styles. (#32)

## [0.2.0] — typed styles

### Changed

- **The `style` argument is typed,** so its accepted values are visible to a
  type checker and an editor rather than only in the docs. (#21)

## [0.1.0] — initial release

### Added

- **Material Design Icons as a font-based provider,** with its asset generation tooling.
