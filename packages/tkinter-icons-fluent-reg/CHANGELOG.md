# Changelog

All notable changes to `tkinter-icons-fluent-reg` are documented in this file.
The base package keeps its own changelog at the root of the repository.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This pack was published as `ttkbootstrap-icons-fluent-reg` through 1.0.x and renamed
to `tkinter-icons-fluent-reg` in 1.1.0. Entries before 1.1.0 were reconstructed from
git history after the fact and are summaries rather than contemporaneous notes.

<!-- release-notes-start -->

## [1.1.0] — measured ink metrics, and the tkinter-icons rename

Requires `tkinter-icons>=5.0.0`. Install it as an extra rather than by name:

```bash
pip install "tkinter-icons[fluent-regular]"
```

### Added

- **`metrics.json`, the measured ink bounds for every glyph in this pack.** The
  5.0.0 renderer centers on true ink instead of on Pillow's `font.getbbox()`,
  which under-reports it on icon fonts. Without this file the pack still
  renders, by falling back to `getbbox`; with it, full-bleed icons keep their
  padding and everything else sits centered. Regenerate with
  `python -m tkinter_icons.tools.generate_metrics fluent-regular` whenever the
  font or glyph map changes. (#67)

### Changed

- **Renamed from `ttkbootstrap-icons-fluent-reg`.** The old distribution is frozen at
  1.0.x and keeps working against a 4.x base package; it will not be updated.
  (#75)

- **The entry point moved to the `tkinter_icons.providers` group.** The base
  package scans the old group as well, so a mixed set of old and new packs stays
  discoverable. (#75)

## [1.0.0] — initial release

### Added

- **The regular weight of Fluent System Icons,** packaged separately from the
  filled set so an app that uses only one does not carry the other's font.
