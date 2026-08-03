"""Per-pack facts and preview strips, both built from the packs themselves.

The sixteen packs used to have a page each, and those pages went stale in
unison: the install line and the import were typed into all sixteen by hand, so
when the extras model landed every one of them was wrong at once. That is the
failure this module exists to prevent — the pages are back, but nothing factual
on them is typed. The install command, the class name, the style list, the glyph
count, the upstream version, and the links all come from `KNOWN_PACKS` and from
the pack's own provider.

What is hand-written is the part a table cannot hold: what a set is *for*, and
what it looks like. The second of those is why per-pack pages earn their keep —
you choose Lucide over Material on drawing weight, and no table expresses that.
So each page shows real glyphs, rendered at build time by this library, from a
curated list of names per pack.

`SHOWCASE`, `SHOWCASE_OVERRIDES`, and `BLURB` are the hand-maintained things
here, and all three are checked: a name that stops resolving raises during the
build, and a pack with no entry warns, which `-W` turns into a failure. They
cannot rot quietly.

Previews are rendered twice, in light and dark ink, and swapped by CSS — the
same approach the family's docs use for screenshots. A single mid-tone would
have avoided the second file at the cost of looking washed out in both themes.
"""

from __future__ import annotations

import importlib
from pathlib import Path

from docutils import nodes
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

logger = logging.getLogger(__name__)

#: Pixel size each glyph is rendered at for the strip. Twice the display size,
#: so the strip stays sharp on a 2x display.
GLYPH_PX = 96

#: Gap between glyphs in the strip, at render scale.
GAP_PX = 32

#: Pixel size and gap for the thumbnail strip on a card, which shows fewer
#: glyphs in a much smaller box than the full preview.
THUMB_PX = 56
THUMB_GAP = 20

#: How many showcase glyphs a card thumbnail shows. Five reads as a sample at
#: card width; eight crushes to nothing.
THUMB_COUNT = 5

#: Ink for each theme. `light`/`dark` name the background, matching the
#: convention `assets/README.md` sets for every other mark in the project.
INK = {"light": "#111827", "dark": "#F9FAFB"}

#: How many glyphs a preview row shows. Six, because six is what fits across
#: the theme's content column without wrapping — eight broke to a row of six
#: and an orphan pair on nearly every page. The row is a sample, not an
#: inventory, so the two it costs are cheap.
PREVIEW_COUNT = 6

#: Representative names per pack, chosen to show what the set is like rather
#: than what it has in common with every other set.
#:
#: Names are written the shortest way that resolves, because the reader copies
#: them: `resolve_icon_name` accepts a pack's own prefix and drops it, so
#: Lucide's `icon-`, Material's `mdi-`, and Fluent's `ic-fluent-` are all
#: optional and none of them earns its width here. Fluent's `-<size>-` segment
#: is not filler and stays.
#:
#: The list has to resolve in *every* one of the pack's styles, because the
#: preview draws one row per style and they are there to be compared — showing
#: a different six per cut would answer a question nobody asked. Where a
#: style's vocabulary genuinely is not the pack's general one, it gets an entry
#: in `SHOWCASE_OVERRIDES` instead.
SHOWCASE: dict[str, list[str]] = {
    "bootstrap": ["house", "gear", "person", "heart", "star", "bell"],
    "devicon": ["python", "javascript", "react", "docker", "git", "linux"],
    "eva": ["home", "search", "settings", "person", "heart", "star"],
    # 32px, because that is the only size Fluent's `light` cut is drawn at and
    # all three cuts have to show the same six for the comparison to mean
    # anything.
    "fluent": ["search-32", "settings-32", "person-32", "chat-32", "delete-32", "clock-32"],
    "fluent-regular": ["home-24", "search-24", "settings-24", "person-24", "heart-24", "star-24"],
    "fontawesome": ["user", "heart", "star", "calendar", "bell", "envelope"],
    "google-material": ["home", "search", "settings", "person", "star", "folder"],
    "ionicons": ["home", "search", "settings", "heart", "star", "person"],
    "lucide": ["house", "search", "settings", "user", "heart", "star"],
    "material": ["home", "folder", "cog", "account", "heart", "star"],
    "meteocons": ["sun", "moon", "cloud", "cloud-sun", "rain", "snow"],
    "remix": ["home", "search", "settings", "user", "heart", "star"],
    "rpg-awesome": ["broadsword", "crossed-swords", "shield", "potion", "dragon", "castle-flag"],
    "simple": ["github", "python", "docker", "rust", "linux", "firefox"],
    "typicons": ["home", "cog", "user", "heart", "star", "download"],
    "weather": ["day-sunny", "cloud", "rain", "snow", "thunderstorm", "fog"],
}

#: Styles whose glyphs are not another cut of the pack's general vocabulary, so
#: the shared list above cannot resolve against them. Two reasons, both facts
#: about the upstream set rather than gaps here:
#:
#: - Font Awesome's ``brands`` is a separate vocabulary. It has no ``user`` and
#:   the interface cuts have no ``github``.
#: - Devicon's ``original`` cuts cover a fraction of the marks its ``plain``
#:   cut does, and the wordmark cuts cover a different fraction again.
#:
#: Fluent used to need one too, back when its showcase spelled the style into
#: every name. It does not: the style argument carries it, so one list of
#: unsuffixed names resolves against all three cuts.
SHOWCASE_OVERRIDES: dict[str, dict[str, list[str]]] = {
    "fontawesome": {
        "brands": ["github", "python", "docker", "apple", "google", "linux"],
    },
    "devicon": {
        "plain-wordmark": ["python", "docker", "git", "nodejs", "java", "mysql"],
        # Avoid stacking React, Electron, and Atom in one row: all three are an
        # orbit around a nucleus, and at this size they read as one mark
        # repeated.
        "original": ["react", "apple", "github", "rust", "redux", "blender"],
        "original-wordmark": ["react", "github", "blender", "go", "bitbucket", "codepen"],
    },
}


#: One line per pack for the card grid on the packs page — what the set is, in
#: the words you would use to tell it apart from its neighbours. Deliberately
#: not a count or a style list: those are on the card already, generated. Kept
#: here rather than typed into sixteen cards so that adding a pack without
#: describing it fails `check_showcase` rather than quietly shipping a blank
#: card.
BLURB: dict[str, str] = {
    "bootstrap": "The Bootstrap project's own set, with an outline and a fill for most icons. Familiar vocabulary if you have written for the web.",
    "devicon": "Language, framework, and tooling marks, each in a plain outline and the logo's own shape, both with optional wordmarks.",
    "eva": "A small, rounded UI set with a matching outline and fill for nearly every icon.",
    "fluent": "Microsoft's system set. The largest here after Material, in three weights, with the design size carried in every name.",
    "fluent-regular": "Fluent's regular weight on its own — the same drawings, one style, a much smaller font.",
    "fontawesome": "The set most people mean when they say icon font, with brand marks alongside the interface glyphs.",
    "google-material": "Google's own icons in four cuts of every glyph: baseline, outlined, round, and sharp.",
    "ionicons": "Ionic's set, drawn for touch targets and a little heavier than most, with outline variants in the names.",
    "lucide": "A light, evenly weighted community set descended from Feather. The most consistent stroke here.",
    "material": "The largest set of all, community-extended well past Google's original. If an icon exists, it is probably here.",
    "meteocons": "Ninety-four hand-drawn weather symbols with a warmer, less systematic feel than the other forecast set.",
    "remix": "A neutral system set drawn on a strict grid, with a line and a fill for everything.",
    "rpg-awesome": "Swords, potions, monsters, and spell effects. For games and character sheets, not toolbars.",
    "simple": "Brand and product marks, thousands of them. Not a UI set — pair it with one.",
    "typicons": "A small, sturdy set from an earlier era of icon drawing, in outline and fill.",
    "weather": "Forecast symbols with day and night variants, plus names that map straight from common weather APIs.",
}


def showcase_for(extra: str, style: str | None) -> list[str]:
    """The glyphs to draw for one pack and style.

    Raises with the fix rather than a bare `KeyError`. `check_showcase` warns
    about a pack with no entry, but a warning is only a build failure under
    `-W`; without this, the next thing a reader saw was a traceback from inside
    a directive rather than the sentence telling them what to add.
    """
    override = SHOWCASE_OVERRIDES.get(extra, {}).get(style)
    if override:
        return override
    try:
        return SHOWCASE[extra]
    except KeyError:
        raise KeyError(
            f"no SHOWCASE entry for pack {extra!r} - add one to "
            f"docs/_ext/pack_showcase.py, listing {PREVIEW_COUNT} icon names "
            f"that resolve in every one of that pack's styles"
        ) from None


def pack_by_extra(extra: str):
    from tkinter_icons.packs import KNOWN_PACKS

    for pack in KNOWN_PACKS:
        if pack.extra == extra:
            return pack
    raise KeyError(f"no pack with extra {extra!r}")


class PackNotInstalled(Exception):
    """The pack's distribution is not importable in this environment.

    Distinguished from every other failure here on purpose. A missing pack is an
    environment problem, and the docs degrade around it the way `packs_table`
    does — a warning, which `-W` turns into a failure for a published build, and
    a gap rather than a crash for a local one. A *name* that no longer resolves
    is content rot and still raises: no build should ever succeed with a blank
    preview in it.
    """


def icon_class(pack):
    try:
        return getattr(importlib.import_module(pack.module), pack.icon_class)
    except ImportError as exc:
        raise PackNotInstalled(pack.extra) from exc


def provider_for(pack):
    try:
        module = importlib.import_module(f"{pack.module}.provider")
    except ImportError as exc:
        raise PackNotInstalled(pack.extra) from exc
    for name, obj in vars(module).items():
        if name.endswith("FontProvider") and name != "BaseFontProvider":
            return obj()
    raise LookupError(f"no provider class in {pack.module}.provider")


def glyph_count(provider) -> int:
    """Total distinct icon names across the provider's styles."""
    index = provider.build_display_index()
    return sum(len(names) for names in index["names_by_style"].values())


def render_one(pack, name: str, style: str | None, ink: str, out: Path, px: int) -> None:
    """Draw a single glyph to its own transparent PNG."""
    from tkinter_icons.iconset import get_icon_set

    cls = icon_class(pack)
    provider = provider_for(pack)
    resolved = provider.resolve_icon_name(name, style)
    glyph = cls.render_pil(resolved, size=px, color=ink, icon_set=get_icon_set(provider, style))
    if glyph.getchannel("A").getbbox() is None:
        raise ValueError(
            f"{pack.extra}: {name!r} rendered nothing in style {style!r}. "
            f"Fix the name in SHOWCASE rather than shipping a blank preview."
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    glyph.save(out)


def render_strip(
    pack,
    names: list[str],
    style: str | None,
    ink: str,
    out: Path,
    px: int = GLYPH_PX,
    gap: int = GAP_PX,
) -> None:
    """Compose one row of glyphs into a transparent PNG.

    Used for the card thumbnails only, where the glyphs are a texture rather
    than a list — nothing is labelled, so one image is cheaper than five.
    """
    from PIL import Image

    from tkinter_icons.iconset import get_icon_set

    cls = icon_class(pack)
    provider = provider_for(pack)
    icon_set = get_icon_set(provider, style)

    width = len(names) * px + (len(names) - 1) * gap
    strip = Image.new("RGBA", (width, px), (0, 0, 0, 0))

    for index, name in enumerate(names):
        resolved = provider.resolve_icon_name(name, style)
        glyph = cls.render_pil(resolved, size=px, color=ink, icon_set=icon_set)
        if glyph.getchannel("A").getbbox() is None:
            raise ValueError(
                f"{pack.extra}: {name!r} rendered nothing in style {style!r}. "
                f"Fix the name in SHOWCASE rather than shipping a blank preview."
            )
        strip.paste(glyph, (index * (px + gap), 0), glyph)

    out.parent.mkdir(parents=True, exist_ok=True)
    strip.save(out)


def render_grid(cells, cols: int, ink: str, out: Path, px: int, gap: int) -> None:
    """Compose glyphs from *different* packs into one grid.

    `render_strip` assumes a single pack and a single style, which is right for
    a preview row. The hero is the opposite: its whole point is that these are
    sixteen unrelated sets drawn by one renderer, so each cell carries its own
    pack.
    """
    from PIL import Image

    from tkinter_icons.iconset import get_icon_set

    rows = (len(cells) + cols - 1) // cols
    width = cols * px + (cols - 1) * gap
    height = rows * px + (rows - 1) * gap
    grid = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    for index, (pack, name) in enumerate(cells):
        provider = provider_for(pack)
        style = provider.default_style
        glyph = icon_class(pack).render_pil(
            provider.resolve_icon_name(name, style),
            size=px, color=ink, icon_set=get_icon_set(provider, style),
        )
        if glyph.getchannel("A").getbbox() is None:
            raise ValueError(f"{pack.extra}: {name!r} rendered nothing for the hero")
        x = (index % cols) * (px + gap)
        y = (index // cols) * (px + gap)
        grid.paste(glyph, (x, y), glyph)

    out.parent.mkdir(parents=True, exist_ok=True)
    grid.save(out)


class IconHeroDirective(SphinxDirective):
    """A band of glyphs, one row per pass over all sixteen packs.

    Usage::

        .. icon-hero::

    The landing page claims sixteen sets behind one renderer; this is that
    sentence drawn rather than asserted, and drawn by the renderer it describes.
    Sampling one glyph per pack per row keeps the sets interleaved, so the band
    reads as a range of drawing styles rather than as blocks of one.
    """

    has_content = False

    #: Starting offset into each pack's showcase, one per row. The offset is
    #: advanced per pack as well, so neighbouring cells are different concepts:
    #: taking a fixed index gave a row of sixteen houses above a row of sixteen
    #: people, which reads as one icon repeated rather than as a range.
    ROWS = (0, 3)

    def run(self):
        from tkinter_icons.packs import KNOWN_PACKS

        note_self(self)
        cells, missing = [], []
        for offset in self.ROWS:
            for position, pack in enumerate(KNOWN_PACKS):
                try:
                    provider = provider_for(pack)
                except PackNotInstalled:
                    if pack.extra not in missing:
                        missing.append(pack.extra)
                    continue
                # The style the cell is *drawn* in, not `None`. `render_grid`
                # draws in `provider.default_style`, so picking names from the
                # general list would break the moment a pack's default style
                # gained an override — which is exactly the case an override
                # exists for, a style the general list cannot resolve against.
                names = showcase_for(pack.extra, provider.default_style)
                cells.append((pack, names[(position + offset) % len(names)]))

        if missing:
            logger.warning(
                "icon-hero: %s not installed, so the hero band is short",
                ", ".join(missing), type="pack_showcase", location=self.get_location(),
            )
        if not cells:
            return []

        cols = len(cells) // len(self.ROWS)
        static = previews_dir(self.env)
        lines = []
        for theme, ink in INK.items():
            render_grid(cells, cols, ink, static / f"hero-{theme}.png", GLYPH_PX, GAP_PX)
            lines += [
                f".. image:: /_static/previews/hero-{theme}.png",
                "   :alt: Glyphs from all sixteen icon packs, drawn by this library",
                f"   :class: icon-hero only-{theme}",
                "",
            ]
        return self.parse_text_to_nodes("\n".join(lines))


def approx(count: int) -> str:
    """A glyph count at the precision a card is read at.

    Cards are scanned to compare magnitudes, and `14,896` next to `2,078` next
    to `94` is three different widths of the same answer. The exact figure is a
    row of the facts table on the pack's own page, and a column of the
    comparison table on the same page as the cards.
    """
    if count < 1000:
        return str(count)
    thousands = count / 1000
    return f"{thousands:.0f}k" if thousands >= 10 else f"{thousands:.1f}k"


def previews_dir(env) -> Path:
    return Path(env.app.srcdir) / "_static" / "previews"


def note_self(directive) -> None:
    """Re-read the page when this module changes.

    Sphinx invalidates a document when the document, or `conf.py`, changes — not
    when an extension does. Everything these directives emit comes from this
    file, so without this an edit to `SHOWCASE` leaves the previously rendered
    strips in place and the build reports success. That happened once, and it is
    invisible: the page is stale rather than broken.
    """
    directive.env.note_dependency(__file__)


def not_installed(directive, extra: str) -> list:
    """Warn that `extra` is missing and render nothing in its place."""
    logger.warning(
        "%s: the %s pack is not installed, so its %s is missing from this page. "
        "Install it before building the published docs: "
        "pip install -e packages/tkinter-icons-<pack>",
        directive.name,
        extra,
        "preview" if "preview" in directive.name else "details",
        type="pack_showcase",
        location=directive.get_location(),
    )
    return []


class PackPreviewDirective(SphinxDirective):
    """Render this pack's showcase glyphs, one labelled row per style.

    Usage::

        .. pack-preview:: material

    Each glyph is its own image with its own name under it, rather than one
    strip with the names listed after it. The strip was ambiguous in two ways
    at once: the names ran together as prose that did not line up with the
    drawings above them, and the style sitting above the row read as a
    thirteenth name rather than as a heading for the row. So the style is
    spelled the way you would pass it, and every name sits under the glyph it
    belongs to.
    """

    required_arguments = 1

    def run(self):
        note_self(self)
        extra = self.arguments[0]
        pack = pack_by_extra(extra)
        try:
            provider = provider_for(pack)
        except PackNotInstalled:
            return not_installed(self, extra)
        # Default style first, whatever order the provider lists them in: the
        # top strip is the one you get from `Icon(name)`, and Bootstrap listing
        # `fill` before its own default `outline` made the first strip the
        # exception rather than the rule.
        styles = sorted(provider.style_list, key=lambda s: s != provider.default_style) or [None]

        static = previews_dir(self.env)
        lines: list[str] = []

        for style in styles:
            names = showcase_for(extra, style)

            if style is not None:
                # Spelled as the argument rather than as a bare word, so it
                # cannot be mistaken for one more icon name.
                default = " (the default)" if style == provider.default_style else ""
                lines += [".. container:: pack-style", "", f'   ``style="{style}"``{default}', ""]

            lines += [".. container:: pack-preview", ""]
            for name in names:
                lines += ["   .. container:: pack-glyph", ""]
                for theme, ink in INK.items():
                    stem = f"{extra}-{style or 'default'}-{name}-{theme}"
                    render_one(pack, name, style, ink, static / f"{stem}.png", GLYPH_PX)
                    lines += [
                        f"      .. image:: /_static/previews/{stem}.png",
                        f"         :alt: {pack.label} {name}",
                        f"         :class: pack-glyph-img only-{theme}",
                        "",
                    ]
                lines += [f"      ``{name}``", ""]

        return self.parse_text_to_nodes("\n".join(lines))


class PackFactsDirective(SphinxDirective):
    """The install line, import, styles, count, and links for one pack.

    Usage::

        .. pack-facts:: material
    """

    required_arguments = 1
    REPO = "https://github.com/israel-dryer/tkinter-icons/blob/main/packages"

    def run(self):
        note_self(self)
        extra = self.arguments[0]
        pack = pack_by_extra(extra)
        try:
            provider = provider_for(pack)
        except PackNotInstalled:
            return not_installed(self, extra)
        count = glyph_count(provider)
        styles = provider.style_list

        # The default is marked rather than listed separately: the question a
        # reader has here is "what do I get if I omit `style`", and that is a
        # property of one entry in the list, not a seventh row.
        style_cell = "none"
        if styles:
            style_cell = ", ".join(
                f"``{s}`` (default)" if s == provider.default_style else f"``{s}``"
                for s in styles
            )

        rows = [
            ("Install", f"``{pack.install_command}``"),
            ("Import", f"``{pack.import_statement}``"),
            ("Icons", f"{count:,}"),
            ("Styles", style_cell),
            ("Upstream version", provider.icon_version or "—"),
            ("Distribution", f"`{pack.distribution} <https://pypi.org/project/{pack.distribution}/>`__"),
        ]
        if pack.alias != pack.icon_class:
            rows.insert(2, ("Also exported as", f"``{pack.icon_class}``"))

        links = []
        if provider.homepage:
            links.append(f"`browse the set <{provider.homepage}>`__")
        if provider.license_url:
            links.append(f"`upstream license <{provider.license_url}>`__")
        links.append(f"`changelog <{self.REPO}/{pack.distribution}/CHANGELOG.md>`__")
        rows.append(("Links", " · ".join(links)))

        lines = [".. list-table::", "   :widths: 30 70", "   :class: pack-facts", ""]
        for label, value in rows:
            lines += [f"   * - {label}", f"     - {value}"]
        lines.append("")
        return self.parse_text_to_nodes("\n".join(lines))


class PackInstallDirective(SphinxDirective):
    """The one command that gets you this pack.

    Usage::

        .. pack-install:: material

    Exists because the facts table moved to the bottom of the page, where it
    belongs — it is a lookup, and a reader works down to it. But the install
    line is not a lookup, it is the thing you came to do, and it was the only
    row of that table with somewhere else to be. The import line did not need
    the same treatment: it is already the first line of every "Using it"
    example, in context.
    """

    required_arguments = 1

    def run(self):
        note_self(self)
        pack = pack_by_extra(self.arguments[0])
        return self.parse_text_to_nodes(
            "\n".join([".. code-block:: bash", "", f"   {pack.install_command}", ""])
        )


class PackCardsDirective(SphinxDirective):
    """The pack catalogue as a grid of cards, each linking to its own page.

    Usage::

        .. pack-cards::

    Generated rather than written out because a seventeenth pack must not be
    able to arrive without a card. Everything on a card except the one-line
    description comes from the catalogue and the live provider; the description
    comes from `BLURB`, which `check_showcase` requires to cover every pack.
    """

    has_content = False

    #: Cards per row at the theme's four breakpoints.
    COLUMNS = "1 2 2 3"

    def run(self):
        from tkinter_icons.packs import KNOWN_PACKS

        note_self(self)
        static = previews_dir(self.env)
        lines = [
            f".. grid:: {self.COLUMNS}",
            "   :gutter: 3",
            "   :class-container: pack-cards",
            "",
        ]

        for pack in KNOWN_PACKS:
            try:
                provider = provider_for(pack)
            except PackNotInstalled:
                not_installed(self, pack.extra)
                continue

            names = showcase_for(pack.extra, provider.default_style)[:THUMB_COUNT]
            for theme, ink in INK.items():
                render_strip(
                    pack, names, provider.default_style, ink,
                    static / f"thumb-{pack.extra}-{theme}.png",
                    px=THUMB_PX, gap=THUMB_GAP,
                )

            lines += [
                f"   .. grid-item-card:: {pack.label}",
                f"      :link: packs/{pack.extra}",
                "      :link-type: doc",
                "",
            ]
            for theme in INK:
                lines += [
                    f"      .. image:: /_static/previews/thumb-{pack.extra}-{theme}.png",
                    f"         :alt: {pack.label} sample glyphs",
                    f"         :class: pack-thumb only-{theme}",
                    "",
                ]
            # Two paragraphs rather than one line: the footer is flexed to put
            # the extra hard left and the count hard right, so a long extra
            # such as `[fluent-regular]` pushes the count away instead of
            # wrapping it onto a second line. The count is abbreviated because
            # a card is for comparing magnitudes — the exact figure is in the
            # table below and on the pack's own page.
            if pack.extra not in BLURB:
                raise KeyError(
                    f"no BLURB entry for pack {pack.extra!r} - add a one-line "
                    f"description to docs/_ext/pack_showcase.py, or the card "
                    f"grid has nothing to say about it"
                )
            lines += [
                f"      {BLURB[pack.extra]}",
                "",
                "      +++",
                f"      ``[{pack.extra}]``",
                "",
                f"      {approx(glyph_count(provider))}",
                "",
            ]

        return self.parse_text_to_nodes("\n".join(lines))


def check_showcase(app, env, docnames):
    """Every pack has a showcase and a blurb, and neither names a pack that is gone."""
    from tkinter_icons.packs import KNOWN_PACKS

    known = {pack.extra for pack in KNOWN_PACKS}
    for label, table in (("SHOWCASE", SHOWCASE), ("BLURB", BLURB), ("SHOWCASE_OVERRIDES", SHOWCASE_OVERRIDES)):
        # Overrides are per-style and optional, so only the reverse check
        # applies to them: a pack may have none, but it may not name one that
        # is gone.
        if label != "SHOWCASE_OVERRIDES":
            missing = sorted(known - set(table))
            if missing:
                logger.warning(
                    "pack_showcase: %s has no entry for %s - add one",
                    label, ", ".join(missing), type="pack_showcase",
                )
        unknown = sorted(set(table) - known)
        if unknown:
            logger.warning(
                "pack_showcase: %s names packs that do not exist: %s",
                label, ", ".join(unknown), type="pack_showcase",
            )

    # A row of a different length than its neighbours is the one thing a
    # reader would read as meaningful and is not, so the count is enforced
    # rather than left to whoever edits the lists next.
    for label, lists in [("SHOWCASE", [(e, n) for e, n in SHOWCASE.items()])] + [
        (f"SHOWCASE_OVERRIDES[{e!r}]", [(s, n) for s, n in by_style.items()])
        for e, by_style in SHOWCASE_OVERRIDES.items()
    ]:
        for key, names in lists:
            if len(names) != PREVIEW_COUNT:
                logger.warning(
                    "pack_showcase: %s[%r] lists %d names; a preview row shows %d",
                    label, key, len(names), PREVIEW_COUNT, type="pack_showcase",
                )

    # An override keyed on a style the pack dropped upstream would silently
    # stop applying, and the general list would start failing to resolve
    # somewhere much further from the cause.
    for extra, by_style in SHOWCASE_OVERRIDES.items():
        if extra not in known:
            continue
        try:
            styles = set(provider_for(pack_by_extra(extra)).style_list)
        except PackNotInstalled:
            continue
        stale = sorted(set(by_style) - styles)
        if stale:
            logger.warning(
                "pack_showcase: SHOWCASE_OVERRIDES[%r] names styles %s that %s does not have",
                extra, ", ".join(stale), extra, type="pack_showcase",
            )


def setup(app):
    app.add_directive("pack-preview", PackPreviewDirective)
    app.add_directive("pack-facts", PackFactsDirective)
    app.add_directive("pack-install", PackInstallDirective)
    app.add_directive("pack-cards", PackCardsDirective)
    app.add_directive("icon-hero", IconHeroDirective)
    app.connect("env-before-read-docs", check_showcase)
    # Parallel-read safe, and it has to say so. Read the Docs builds with
    # `-j auto -W`, which turns "the pack_showcase extension is not safe for
    # parallel reading" into a failed build — the docs themselves being clean
    # is beside the point once a warning is an error.
    #
    # The claim holds because nothing here is shared across workers. The three
    # tables are read-only constants. Every rendered file's name is derived from
    # (extra, style, name, theme), and each is written by exactly one document:
    # a pack's previews only by its own page, the thumbnails only by packs.rst,
    # the hero band only by index.rst — so no two workers write the same path.
    # `mkdir(parents=True, exist_ok=True)` tolerates the race on the shared
    # directory itself, and the completeness check runs on `env-before-read-docs`,
    # which fires once in the parent.
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
