# Brand assets

Source of truth for the project's marks: the docs site, the GitHub repository,
and the package READMEs. Not used at runtime — nothing here ships in a wheel.

Note there are two other directories called `assets` in this repository, and
neither is this one: `docs/assets/` holds documentation screenshots, and
`packages/*/src/*/assets/` holds fonts and glyph data that *does* ship.

## What is here

| File | For |
|---|---|
| `icon.svg` | the square mark, standard weight |
| `icon-small.svg` | same mark redrawn for small sizes — fuller bleed, chunkier star, so it survives 16px |
| `logo-compact-{light,dark}.svg` | two stacked squares |
| `logo-full-{light,dark}.svg` | three stacked squares |
| `png/icon-{16,32,48,64,128,180,256,512}.png` | rasterised mark, transparent background |
| `png/wordmark-{light,dark}.png` | mark + wordmark, 948×228 |
| `png/github-social-1280x640.png` | the repository social card |

`light` and `dark` name the **background the asset is drawn for**, not the ink:
`wordmark-light` is dark ink on white, `wordmark-dark` is light ink on navy.

## Palette

Teal primary on a Tailwind neutral ramp. This is deliberately **not** bootstack's
palette, which is Bootstrap blue (`#0d6efd`) primary with teal only as an accent,
on Bootstrap grays. The two projects share tooling and conventions, not an
identity — Bootstrap icons are built into ttkbootstrap and bootstack, and this
library is for people who are not using either.

| Role | Light | Dark |
|---|---|---|
| Logo mark | `#0F9488` | `#0F9488` |
| Link / primary | `#0F766E` | `#2DD4BF` |
| Background | `#FFFFFF` | `#111827` |
| Body text | `#111827` | `#F9FAFB` |
| Muted | `#4B5563` | `#9CA3AF` |
| Border | `#D1D5DB` | `#374151` |

**Do not use `#0F9488` as a link or primary colour.** It is 3.74:1 on white and
4.12:1 on a dark background — below WCAG AA's 4.5:1 in *both* modes, sitting in
the middle where neither works. It is fine on the mark itself, which WCAG 1.4.3
exempts as a logotype. The two link values above are the same hue one step out
in each direction, at 5.47:1 and 8.29:1.

`#2DD4BF` is a point away from bootstack's dark accent `#2DD4AA`, so the two
sites' dark modes still read as related without this one borrowing the blue.

## Where copies go

Each consumer needs the file somewhere specific, so these are copies, not
references. Update here first, then the copy.

| Consumer | Copy at | Why not a reference |
|---|---|---|
| Sphinx docs | `docs/_static/` | `html_static_path` does not reach outside the docs tree |
| Package READMEs | absolute `raw.githubusercontent.com` URL | PyPI resolves no relative paths |
| GitHub social card | uploaded under Settings → General | never a file in the tree |

## Backgrounds are baked into the wordmarks

The icon PNGs are transparent. **The wordmark PNGs and the social card are
not** — they carry an opaque `#FFFFFF` or `#111827` field.

That is right for a README, where an opaque banner reads as deliberate on any
page. It is wrong for a docs navbar, where anything but an exact background
match shows as a visible rectangle. A navbar logo wants a transparent SVG.

## Using a wordmark in a README

A README is rendered twice — by GitHub, which has a dark mode, and by PyPI,
which does not. One opaque image cannot serve both. `<picture>` can:

```html
<picture>
  <source media="(prefers-color-scheme: dark)"
          srcset="https://raw.githubusercontent.com/israel-dryer/tkinter-icons/main/assets/png/wordmark-dark.png">
  <img alt="tkinter-icons"
       src="https://raw.githubusercontent.com/israel-dryer/tkinter-icons/main/assets/png/wordmark-light.png"
       width="420">
</picture>
```

PyPI's renderer keeps `<picture>` and `<img>` but strips `<source>`, so it falls
through to the light wordmark — correct, since PyPI pages are always light.
GitHub honours both. Verified against `readme_renderer`, which is what PyPI runs
and what `twine check` uses.

**PNG, not SVG, in a README.** `raw.githubusercontent.com` serves `.svg` as
`text/plain`, so an `<img>` pointing at one renders nothing on a PyPI page.
