# Brand assets

Source of truth for the project's marks: the docs site, the GitHub repository,
and the package READMEs.

One pair is **copied** into a wheel: `png/icon-32.png` and `png/icon-64.png` are
duplicated at `packages/tkinter-icons/src/tkinter_icons/assets/` and used as the
icon browser's window icon. Copies rather than references, because package data
cannot reach outside its own package — the same arrangement as the wordmarks in
`docs/_static/`. Update here first, then the copy. Nothing else here is used at
runtime.

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
| `wordmark-{light,dark}.svg` | mark + wordmark, teal accent on the hyphen |
| `wordmark-mono-{light,dark}.svg` | same, single ink — no teal accent |
| `png/icon-{16,32,48,64,128,180,256,512}.png` | rasterised mark |
| `png/wordmark-{light,dark}.png` | rasterised wordmark, 852×192 |
| `png/github-social-1280x640.png` | the repository social card |

The wordmark SVGs carry **outlined text, not `<text>`**. Keep it that way. The
letterforms are JetBrains Mono, and an SVG used as a logo is loaded as its own
image document — it cannot see `@font-face` rules from the page embedding it, so
live text falls back to whatever local monospace the reader happens to have.
Outlines also keep a font binary out of the repository.

`light` and `dark` name the **background the asset is drawn for**, not the ink it
uses. `wordmark-light` is dark ink for a light page; `wordmark-dark` is light ink
for a dark one. Both are transparent, so picking the wrong one does not show a
mismatched box — it shows almost nothing.

## Palette

Teal primary on a Tailwind neutral ramp. This is deliberately **not** bootstack's
palette, which is Bootstrap blue (`#0d6efd`) primary with teal only as an accent,
on Bootstrap grays. The two projects share tooling and conventions, not an
identity, and never shared a lineage — Bootstrap icons are built into
ttkbootstrap, and this library is for people who are not using it.

| Role | Light | Dark |
|---|---|---|
| Logo mark | `#0F9488` | `#0F9488` |
| Link / primary | `#0F766E` | `#2DD4BF` |
| Background | `#FFFFFF` | `#111827` |
| Body text | `#111827` | `#F9FAFB` |
| Muted | `#4B5563` | `#9CA3AF` |
| Border | `#D1D5DB` | `#374151` |

**Do not use `#0F9488` as a link or primary color.** It is 3.74:1 on white and
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

## Everything is transparent except the social card

Only `github-social-1280x640.png` carries an opaque field, which is correct — it
is a standalone card, not a mark placed on someone else's background.

The marks and wordmarks are all transparent, so `light` and `dark` select ink to
suit the page rather than dragging a background along. That is what a docs
navbar needs, and it is what makes the `<picture>` pattern below work: each
variant sits on the reader's actual background instead of a baked slab that only
matches one of them.

## Using a wordmark in a README

A README is rendered twice — by GitHub, which has a dark mode, and by PyPI,
which does not. Each wordmark reads on only one of those backgrounds, so no
single file serves both. `<picture>` does:

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
GitHub honors both. Verified against `readme_renderer`, which is what PyPI runs
and what `twine check` uses.

**PNG, not SVG, in a README.** `raw.githubusercontent.com` serves `.svg` as
`text/plain`, so an `<img>` pointing at one renders nothing on a PyPI page.
