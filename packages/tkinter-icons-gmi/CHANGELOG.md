# Changelog

All notable changes to `tkinter-icons-gmi` are documented in this file.
The base package keeps its own changelog at the root of the repository.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This pack was published as `ttkbootstrap-icons-gmi` through 1.0.x and renamed
to `tkinter-icons-gmi` in 1.1.0. Entries before 1.1.0 were reconstructed from
git history after the fact and are summaries rather than contemporaneous notes.

<!-- release-notes-start -->

## [1.1.2] — three styles stop advertising glyphs their fonts do not have

No font change and no metrics change. What changed is the glyph maps for `outlined`, `round` and `sharp`, which listed names those fonts never carried.

### Changed

- **43 names are gone from `outlined`, and 38 each from `round` and `sharp`.** They never drew anything: each one was mapped to a codepoint its style's font does not contain, so asking for it produced a fully transparent image with no exception and no warning. Asking for one now raises `ValueError` from the constructor, and `render_pil` raises the same — which is the intended improvement, but it is a behavior change for anyone who was calling one of these and accepting the blank. **All 43 still draw in `baseline`**, which is this pack's default style and was never affected. Seven have a plain spelling the affected style does carry, so `info_outline` is `info` there, and likewise `drive_file_move`, `label`, `label_important`, `lightbulb`, `lock` and `workspaces`. The other 36 have no substitute in these three styles at all. (#140)

  The 43 distinct names, across the three styles: `add_call`, `assignment_add`, `assistant_navigation`, `barcode_reader`, `block_flipped`, `cloudy_snowing`, `conveyor_belt`, `dew_point`, `drive_file_move_outline`, `edit_document`, `edit_square`, `file_upload_off`, `filter_list_alt`, `fire_hydrant`, `foggy`, `forklift`, `format_list_bulleted_add`, `front_loader`, `goat`, `home_filled`, `info_outline`, `keyboard_command`, `keyboard_option`, `label_important_outline`, `label_outline`, `lightbulb_outline`, `location_pin`, `lock_outline`, `movie_edit`, `no_meals_ouline`, `outgoing_mail`, `pallet`, `pie_chart_outlined`, `rebase_edit`, `shelves`, `snowing`, `sunny`, `sunny_snowing`, `trolley`, `volume_down_alt`, `wb_twighlight`, `workspaces_filled`, `workspaces_outline`. 38 of them were absent from all three styles. The remaining five are `_outline` spellings — `info_outline`, `label_important_outline`, `label_outline`, `lightbulb_outline`, `lock_outline` — and only `outlined` was advertising them: the `round` and `sharp` fonts do carry those five, and the `outlined` font is the one cut where a separate outlined variant of an icon would be redundant.

  All four styles reporting an identical name count was the visible symptom, and it had been true since the pack was first built.

### Fixed

- **The generator no longer publishes one style's codepoints as every style's.** It downloaded the *baseline* codepoints file and wrote it verbatim to all four glyph maps, under a comment asserting that Material Icons use the same codepoints across all styles. They do not. Each style's glyph map is now built against the font that style is actually drawn from, so a regeneration cannot reintroduce this. (#140)

## [1.1.1] — corrected style list, and an intro in this library's voice

No glyph, font or metrics change: this release exists to correct text that PyPI freezes at release time.

### Fixed

- **This pack does not ship a `twotone` style, and claimed it did in two places.** The distribution summary and the README intro both listed it; the styles are baseline, outlined, round and sharp. (#111)

### Changed

- **The README intro and the distribution summary are written from this library's side rather than upstream's.** They now say what the set covers and when to reach for it, instead of repeating the upstream project's own description of the font. (#120)

## [1.1.0] — measured ink metrics, and the tkinter-icons rename

Requires `tkinter-icons>=5.0.0`. Install it as an extra rather than by name:

```bash
pip install "tkinter-icons[google-material]"
```

### Added

- **`metrics.json`, the measured ink bounds for every glyph in this pack.** The
  5.0.0 renderer centers on true ink instead of on Pillow's `font.getbbox()`,
  which under-reports it on icon fonts. Without this file the pack still
  renders, by falling back to `getbbox`; with it, full-bleed icons keep their
  padding and everything else sits centered. Regenerate with
  `python -m tkinter_icons.tools.generate_metrics gmi` whenever the font or
  glyph map changes. (#67)

- **The icon class takes `options`.** `RenderOptions` carries every drawing knob — padding, oversampling, sharpening, even-snapping — and was reachable only through `Icon.render_pil` or the base `Icon`, not through the class you actually construct. `GMatIcon("name", size=32, options=RenderOptions(pad_factor=0.0))` now works. Keyword-only, so it cannot be confused with `style`.

- **`render_pil` works on this class without a warm-up.** It read an icon set shared by every subclass, so `GMatIcon.render_pil(...)` drew this pack's glyphs only if something had already constructed one of its icons — and raised in a fresh process. The class names its own provider now, and resolves friendly names the way the constructor does.

### Changed

- **Renamed from `ttkbootstrap-icons-gmi`.** The old distribution is frozen at
  1.0.x and keeps working against a 4.x base package; it will not be updated.
  (#75)

- **The entry point moved to the `tkinter_icons.providers` group.** The base
  package scans the old group as well, so a mixed set of old and new packs stays
  discoverable. (#75)

## [1.0.1] — icon references

### Fixed

- **Invalid icon references** in the shipped name list. (#46)

### Removed

- **The `tkicons-gmi-build` and `tkicons-gmi-quick` commands, and the
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

- **Google Material Icons as a font-based provider,** with its asset generation tooling.
