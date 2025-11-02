# Contributing

Thanks for helping improve ttkbootstrap-icons! Contributions are welcome for both the core package and additional icon providers.

This guide focuses on adding a new font-based provider package and what (if anything) needs to change in the base package and documentation.

---

## Overview: How providers work

External providers are discovered via Python entry points (group: `ttkbootstrap_icons.providers`). The base package’s registry loads each entry point and the Icon Browser lists all discovered providers. Because of this, most new providers do not require changes to the core code.

At build time, the site documentation pulls each provider’s README into `providers/` using `mkdocs-gen-files`.

---

## Add a new provider package

Follow this pattern under `packages/`:

```
packages/
  ttkbootstrap-icons-<slug>/
    pyproject.toml
    README.md
    src/
      ttkbootstrap_icons_<slug>/
        provider.py
        icon.py                 # optional convenience wrapper class
        glyphmap.json           # or glyphmap-<style>.json files
        fonts/                  # provider font files
        LICENSES/               # upstream license texts (required)
```

### 1) Package metadata (`pyproject.toml`)

- Name: `ttkbootstrap-icons-<slug>`
- Entry point (required):

```toml
[project.entry-points."ttkbootstrap_icons.providers"]
<slug> = "ttkbootstrap_icons_<slug>.provider:YourProviderClass"
```

Tip: make sure the class name matches the actual exported class (e.g., `TypiconsFontProvider`).

### 2) Provider class (`provider.py`)

Subclass `BaseFontProvider` and set the required fields.

```python
from ttkbootstrap_icons.providers import BaseFontProvider

class YourProviderClass(BaseFontProvider):
    def __init__(self):
        super().__init__(
            name="<slug>",
            display_name="Display Name",
            package="ttkbootstrap_icons_<slug>",
            # For a single font file:
            filename="fonts/<fontfile>.ttf",
            # OR for style-based providers (same or different font files):
            default_style="fill",  # example
            styles={
                "fill":    {"filename": "fonts/<fontfile>.ttf", "predicate": YourProviderClass._is_fill},
                "outline": {"filename": "fonts/<fontfile>.ttf", "predicate": YourProviderClass._is_outline},
            },
            homepage="https://...",
            license_url="https://...",
            icon_version="<icon-set-version>",
            # optional tuning
            pad_factor=0.10,
            y_bias=0.0,
            scale_to_fit=True,
        )

    @staticmethod
    def _is_fill(name: str) -> bool:
        return name.endswith("-fill")  # example

    @staticmethod
    def _is_outline(name: str) -> bool:
        return name.endswith("-outline")
```

Notes
- Single-file providers: include `filename` and a single `glyphmap.json`.
- Style providers: omit `filename` and provide `styles` with a `predicate` per style and `glyphmap-<style>.json` for each.
- `icon_version` should reflect the upstream icon set version for display in the browser and docs.
- You may override `format_glyph_name()` if you need to normalize upstream naming.

### 3) Glyph map and fonts

- Put the font files under `fonts/`.
- Include one or more glyph maps:
  - Single-file: `glyphmap.json`
  - Per-style: `glyphmap-<style>.json` files
- Glyph map keys are the raw glyph names; the provider resolves friendly names to them.

### 4) Optional convenience class (`icon.py`)

Provide a thin wrapper that resolves names with your provider, then calls the base `Icon`.

```python
from ttkbootstrap_icons.icon import Icon
from ttkbootstrap_icons_<slug>.provider import YourProviderClass

class YourIcon(Icon):
    def __init__(self, name: str, size: int = 24, color: str = "black", **kwargs):
        prov = YourProviderClass()
        YourIcon.initialize_with_provider(prov)
        resolved = prov.resolve_icon_name(name, **kwargs)
        super().__init__(resolved, size, color)
```

### 5) README and licenses

- Add `README.md` following the standardized sections (Install, Quick start, Styles, Icon Browser, License and Attribution). Include a local `browser.png` screenshot if desired.
- Add upstream license texts under `LICENSES/` and note them in your README.

---

## Testing your provider

Install your provider locally and run the browser:

```bash
pip install -e packages/ttkbootstrap-icons-<slug>
python -m ttkbootstrap_icons.browser
```

Verify discovery via entry points:

```bash
python -c "from importlib.metadata import entry_points; print([ (e.name, e.value) for e in entry_points(group='ttkbootstrap_icons.providers') ])"
```

If the provider doesn’t appear, check:
- The entry point target points to a valid, importable class.
- The module/package layout matches `pyproject.toml` (`package-dir = { "" = "src" }`).

---

## Base package updates (when needed)

The core app auto-discovers providers. You generally do not need code changes in the base package.

Documentation additions:
- Providers nav: add your provider page to `mkdocs.yml` (Providers section) if you want it in the sidebar.
- Generation map: add your package to `scripts/gen_providers_docs.py` (`PACKAGE_TO_DOC`) so your README is pulled into `docs/providers/` at build time. Also update the display name map inside `_generate_providers_table()` if needed.
- Licenses: add your project to `THIRD-PARTY-NOTICES.md` and ensure the table in `docs/license.md` includes it (Name, Package, License link). Maintainers may help keep this in sync.

---

## Naming conventions

- PyPI package: `ttkbootstrap-icons-<slug>` (lowercase, hyphenated)
- Python package: `ttkbootstrap_icons_<slug>` (lowercase, underscore)
- Provider class: `<Name>FontProvider` (e.g., `RemixFontProvider`, `TypiconsFontProvider`)
- Icon class (optional): `<Name>Icon` (e.g., `FAIcon`, `RemixIcon`)
- Entry point key: `<slug>` (lowercase); this is how the registry lists your provider.

---

## Tips

- Keep glyph maps minimal and accurate; favor style-specific maps if upstream uses suffixes (e.g., `-line`, `-fill`).
- Validate names in the Icon Browser; try searching and copying names to ensure style handling is correct.
- Prefer stable upstream links in your README and include a `browser.png` for docs.
