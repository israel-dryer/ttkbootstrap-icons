"""Figures that draw what the renderer pages assert, using the renderer.

`sizing-and-quality` described measured ink, padding, oversampling and
even-snapping entirely in prose. Every one of those claims is a side-by-side
render, and a reader had no way to check any of them — which is how the page
came to carry a claim about the fallback centering path that measurement does
not support. Prose cannot be wrong quietly once the picture is beside it.

So the figures are drawn at build time, by this library, from the packs that are
installed. Nothing here is a screenshot, so nothing here goes stale: change the
renderer and the pictures change with it, or the build fails.

`pack_showcase` is the sibling module and the pattern — same light/dark pair,
same `only-light`/`only-dark` swap, same rule that a name which stops resolving
raises rather than shipping a blank. What is different is *why* the images
exist. A showcase strip shows a set; these show one glyph drawn several ways,
so the difference between panels is the whole content and everything else has
to be held constant.

Two mechanics follow from that.

**These call `render_glyph` directly, not `Icon.render_pil`.** The measured-ink
figure needs the `ink=None` path, and no public entry point offers it — that is
correct, since it is a fallback for packs without metrics, not a mode.

**A figure about small sizes is drawn small and then magnified with
nearest-neighbour.** The oversampling claim is about what happens at 16 pixels,
so a figure rendered at 96 and shrunk by CSS would demonstrate nothing. Such a
panel is rendered at its real size and blown up by an integer factor with no
interpolation, so the pixels a reader sees are the pixels the renderer wrote,
and `custom.css` applies `image-rendering: pixelated` to *those* panels only.
The figures read at their own size must not get that rule — they are displayed
1:1, and pixelating them would let any zoom or non-integer device pixel ratio
turn their antialiased edges blocky, in figures whose whole subject is render
quality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

# Imported rather than redeclared, and `PackNotInstalled` is why. Two modules
# each defining a class of that name produce two unrelated exceptions, so
# `except render_figures.PackNotInstalled` would not catch what
# `pack_showcase.provider_for` raises — a figure would stop degrading to a
# warning and start crashing the build with a traceback. That trap only opens
# once someone reaches for one more helper from the sibling module, which is
# exactly what `save_atomic` already made natural. `INK` is shared for a
# smaller reason: figures and previews appear on the same pages and have to sit
# at the same weight.
from pack_showcase import INK, PackNotInstalled, pack_by_extra, provider_for, save_atomic

logger = logging.getLogger(__name__)

#: Guide lines — the frame and the padded box — drawn at this alpha over the
#: theme's ink. Visible enough to read as a boundary, faint enough that the
#: glyph stays the subject.
GUIDE_ALPHA = 90


@dataclass(frozen=True)
class Panel:
    """One cell of a figure: the same glyph under one set of conditions.

    `options` is merged onto the pack's own defaults rather than replacing
    them, so a panel changing `pad_factor` does not silently also change the
    oversampling the pack asked for.
    """

    caption: str
    options: dict = field(default_factory=dict)
    #: False draws through `_place_by_bbox`, the fallback for a pack that ships
    #: no metrics. There is no public way to ask for this, which is the point.
    ink: bool = True


@dataclass(frozen=True)
class Figure:
    """One glyph drawn several ways, with the panels side by side."""

    pack: str
    name: str
    panels: tuple[Panel, ...]
    alt: str
    style: str | None = None
    size: int = 96
    #: Nearest-neighbour magnification. 1 for figures read at their own size.
    zoom: int = 1
    #: "frame" outlines the image; "pad" outlines the padded box inside it.
    guides: tuple[str, ...] = ()


#: The figures, keyed by the name a page passes to `.. renderer-figure::`.
#:
#: **Every subject here was picked by measuring, not by taste**, and the first
#: attempt at each of these was wrong:
#:
#: - The ink figure first used a Font Awesome glyph, chosen from a sweep run
#:   with the *default* `RenderOptions`. Font Awesome's provider asks for
#:   `pad_factor=0.15`, so with its own options the two panels came out nearly
#:   identical. The subjects below are the extremes under each pack's real
#:   options, censused over the whole glyph map of the style each figure draws:
#:   Eva fills 79% of the padded box on the fallback path against 100% on the
#:   measured one, and Weather sits a median 10.0 px off-center at 96 px.
#: - Those two figures were first written down as 73%/94% and 10.5 px, from a
#:   400-name sample rather than a census. Sampling is fine for ranking
#:   candidates and not fine for a number anyone will quote — and the 10.5 then
#:   contradicted the page's own "a median 10 pixels". Both now come from
#:   `.github/scripts/generate_placement_census.py`, which is also where "fill"
#:   and "off-center" are defined; quoting either without its definition is how
#:   the same two numbers came to be restated three times and reconciled none.
#: - The oversampling figure first used Material's `cog`, which is heavy enough
#:   to survive without oversampling. Bootstrap's `gear` is a hairline and
#:   turns to gray mush, which is what the claim is about.
#:
#: A figure whose panels look alike argues against the prose beside it, so
#: check a new one by eye before adding it.
FIGURES: dict[str, Figure] = {
    "measured-ink": Figure(
        pack="eva",
        name="home",
        panels=(
            Panel("measured ink — 5.0 and later", ink=True),
            Panel("``getbbox`` — the no-metrics fallback", ink=False),
        ),
        guides=("frame", "pad"),
        alt="One glyph fitted to measured ink, and fitted smaller by getbbox",
    ),
    "measured-ink-centering": Figure(
        pack="weather",
        name="thunderstorm",
        panels=(
            Panel("measured ink", ink=True),
            Panel("``getbbox``, riding the font's ascent", ink=False),
        ),
        guides=("frame",),
        alt="One glyph centered on its ink, and pushed against the top of the frame by getbbox",
    ),
    "padding": Figure(
        pack="lucide",
        name="house",
        panels=(
            Panel("``pad_factor=0.0``", options={"pad_factor": 0.0}),
            Panel("``0.10`` — the default", options={"pad_factor": 0.10}),
            Panel("``0.25``", options={"pad_factor": 0.25}),
        ),
        guides=("frame", "pad"),
        alt="One glyph at three padding factors, with the padded box drawn",
    ),
    # Rendered at the size the claim is about and magnified, because at 16
    # pixels shown as 16 pixels the difference is real and far too small to
    # argue about on a documentation page.
    "oversampling": Figure(
        pack="bootstrap",
        name="gear",
        size=16,
        zoom=6,
        panels=(
            Panel(
                "``oversample=1``, no sharpen",
                options={"oversample": 1, "sharpen": False},
            ),
            Panel("the default — 3× and a light sharpen"),
        ),
        alt="A 16-pixel glyph drawn directly, and drawn oversampled then downscaled",
    ),
}

# There is deliberately no figure for even-snapping. The claim is that an odd
# pixel size lands the glyph on a half-pixel boundary *at fractional display
# scaling*, and a PNG in a browser cannot reproduce a 150% Windows scale
# factor — a 15 px render beside a 16 px one shows two sizes of the same icon
# and nothing about blur. Drawn, looked at, and dropped: a figure that does not
# show its claim quietly argues against it.


#: The same five concepts drawn by five packs, for `choosing-a-pack`.
#:
#: Each pack is drawn in its *default* style, because that is what
#: `LucideIcon("house")` gives you and the question the page answers is which
#: pack to install. That the row weights differ so much — Lucide's hairline
#: outline against Material's solid fill — is the comparison, not a flaw in it.
#:
#: Names are per pack because vocabularies are: Material calls the gear ``cog``
#: and Font Awesome calls search ``magnifying-glass``. Nothing here can be
#: derived, so all of it is checked at build time instead.
COMPARISON_PACKS = ("lucide", "bootstrap", "remix", "material", "fontawesome")

COMPARISON_ROWS: tuple[tuple[str, dict[str, str]], ...] = (
    ("home", {"lucide": "house", "bootstrap": "house", "remix": "home",
              "material": "home", "fontawesome": "house"}),
    ("search", {"lucide": "search", "bootstrap": "search", "remix": "search",
                "material": "magnify", "fontawesome": "magnifying-glass"}),
    ("settings", {"lucide": "settings", "bootstrap": "gear", "remix": "settings",
                  "material": "cog", "fontawesome": "gear"}),
    ("user", {"lucide": "user", "bootstrap": "person", "remix": "user",
              "material": "account", "fontawesome": "user"}),
    ("star", {"lucide": "star", "bootstrap": "star", "remix": "star",
              "material": "star", "fontawesome": "star"}),
)

#: Size the comparison grid is drawn at. Twice the display height, so it stays
#: sharp on a 2x screen — the same trade `pack_showcase` makes.
COMPARISON_PX = 72


def figures_dir(env) -> Path:
    return Path(env.app.srcdir) / "_static" / "figures"


def note_self(directive) -> None:
    """Re-read the page when either extension module changes.

    Sphinx invalidates a document when the document changes, not when an
    extension does — so without this, editing `FIGURES` leaves the previously
    rendered PNGs in place and the build reports success. `pack_showcase` was
    caught by exactly this once, and the symptom is a stale page rather than a
    broken one.

    Deliberately *not* imported from `pack_showcase` along with the rest.
    `__file__` there is that module, so the imported version would register the
    wrong dependency and reintroduce the bug it exists to prevent. Both files
    are noted because `INK` and `save_atomic` come from over there, so a change
    to either one changes what these figures look like.
    """
    directive.env.note_dependency(__file__)
    directive.env.note_dependency(pack_showcase_file())


def pack_showcase_file() -> str:
    import pack_showcase

    return pack_showcase.__file__


def not_installed(directive, extra: str) -> list:
    logger.warning(
        "%s: the %s pack is not installed, so this figure is missing. "
        "Install it before building the published docs: "
        "pip install --no-deps -e packages/tkinter-icons-<pack>",
        directive.name, extra, type="render_figures", location=directive.get_location(),
    )
    return []


def padded_box_inset(options, base_size: int, zoom: int) -> int:
    """Where the padded box actually falls, in displayed pixels.

    This has to reproduce `render_glyph`'s arithmetic rather than approximate
    it. The first version computed `round(width * pad_factor)`, and the
    renderer computes `int(canvas_size * pad_factor)` — at 96 px and
    `pad_factor=0.10` that is 10 against 9, so the guide was drawn one pixel
    inside the box it claimed to mark and the exemplar glyph, correctly fitted
    to rows 9–86, crossed its own guide on both edges. A figure whose caption
    says "what the ink is supposed to fill" cannot have the ink spilling out of
    it.

    The padding is applied in oversampled space and the image is downscaled
    afterwards, so the boundary comes back to final-image pixels through
    `oversample` before the figure's own magnification is applied.
    """
    from tkinter_icons.render import auto_oversample, snap_size

    snapped = snap_size(base_size, snap_even=options.snap_even)
    oversample = max(1, int(options.oversample or auto_oversample(snapped)))
    pad_oversampled = int(snapped * oversample * options.pad_factor)
    return round(pad_oversampled / oversample * zoom)


def draw_guides(image, guides: tuple[str, ...], options, base_size: int, zoom: int, ink: str):
    """Outline the frame, and optionally the padded box inside it.

    Without these, `pad_factor=0.0` beside `pad_factor=0.25` is just two sizes
    of the same house and the reader has nothing to measure them against. The
    frame is what `size` means and the inner box is what the glyph is fitted
    to, so drawing both turns the figure into the definition.
    """
    from PIL import Image, ImageDraw

    if not guides:
        return image

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    red, green, blue = Image.new("RGB", (1, 1), ink).getpixel((0, 0))
    stroke = (red, green, blue, GUIDE_ALPHA)
    edge = image.size[0] - 1

    if "frame" in guides:
        draw.rectangle((0, 0, edge, edge), outline=stroke, width=1)
    if "pad" in guides and options.pad_factor > 0:
        inset = padded_box_inset(options, base_size, zoom)
        draw.rectangle((inset, inset, edge - inset, edge - inset), outline=stroke, width=1)

    return Image.alpha_composite(image, overlay)


def build_panel(pack, figure: Figure, panel: Panel, ink_color: str):
    """Draw one panel and return it, magnified if the figure asks for it.

    Separate from writing it so `tests/test_render_figures.py` can compare two
    panels without a Sphinx build. That test is the one thing standing between
    this module and a figure whose panels look identical — which is not a build
    failure, just a picture that quietly argues against the paragraph above it.
    """
    from PIL import Image

    from tkinter_icons.iconset import get_icon_set
    from tkinter_icons.render import render_glyph

    provider = provider_for(pack)
    style = figure.style if figure.style is not None else provider.default_style
    icon_set = get_icon_set(provider, style)
    resolved = provider.resolve_icon_name(figure.name, style)
    glyph = icon_set.glyph(resolved)
    if glyph is None:
        raise ValueError(
            f"{figure.pack}: {figure.name!r} resolved to {resolved!r}, which is not "
            f"in the {style!r} icon set. Fix the name in FIGURES rather than "
            f"shipping a blank panel."
        )

    options = icon_set.options.merge(**panel.options) if panel.options else icon_set.options
    image = render_glyph(
        glyph,
        figure.size,
        ink_color,
        font_key=icon_set.font_key,
        font_bytes=icon_set.font_bytes,
        ink=icon_set.ink(resolved) if panel.ink else None,
        options=options,
    )
    if image.getchannel("A").getbbox() is None:
        raise ValueError(
            f"{figure.pack}: {figure.name!r} rendered nothing for panel "
            f"{panel.caption!r}. A figure that shows an empty square is worse "
            f"than no figure."
        )

    if figure.zoom > 1:
        size = image.size[0] * figure.zoom
        image = image.resize((size, size), Image.NEAREST)

    return draw_guides(image, figure.guides, options, figure.size, figure.zoom, ink_color)


def render_panel(pack, figure: Figure, panel: Panel, ink_color: str, out: Path) -> None:
    """Draw one panel and write it."""
    save_atomic(build_panel(pack, figure, panel, ink_color), out)


class RendererFigureDirective(SphinxDirective):
    """One glyph drawn several ways, panels side by side.

    Usage::

        .. renderer-figure:: measured-ink

    The key names an entry in `FIGURES`. Everything about the figure — which
    pack, which glyph, what each panel changes, and how the captions read — is
    defined there rather than in the page, so a claim and its picture cannot
    drift apart in different files.
    """

    required_arguments = 1

    def run(self):
        note_self(self)
        key = self.arguments[0]
        try:
            figure = FIGURES[key]
        except KeyError:
            raise self.error(
                f"no figure named {key!r}. Add one to FIGURES in "
                f"docs/_ext/render_figures.py; the ones defined are "
                f"{', '.join(sorted(FIGURES))}."
            )

        pack = pack_by_extra(figure.pack)
        try:
            provider_for(pack)
        except PackNotInstalled:
            return not_installed(self, figure.pack)

        static = figures_dir(self.env)
        # Only a magnified panel gets `pixelated`. The unmagnified ones are
        # displayed 1:1, where the rule would let browser zoom or a fractional
        # device pixel ratio blockify antialiased edges — in figures whose
        # subject is render quality.
        zoomed = " render-img-zoomed" if figure.zoom > 1 else ""
        lines = [".. container:: render-figure", ""]
        for index, panel in enumerate(figure.panels):
            lines += ["   .. container:: render-panel", ""]
            for theme, ink_color in INK.items():
                stem = f"{key}-{index}-{theme}"
                render_panel(pack, figure, panel, ink_color, static / f"{stem}.png")
                lines += [
                    f"      .. image:: /_static/figures/{stem}.png",
                    f"         :alt: {figure.alt}",
                    f"         :class: render-img{zoomed} only-{theme}",
                    "",
                ]
            lines += [f"      {panel.caption}", ""]

        return self.parse_text_to_nodes("\n".join(lines))


class PackComparisonDirective(SphinxDirective):
    """The same five concepts drawn by five packs, one row each.

    Usage::

        .. pack-comparison::

    "Sets are not interchangeable visually" is the load-bearing sentence on
    `choosing-a-pack`, and a table cannot carry it. This is that sentence
    drawn.
    """

    has_content = False

    def run(self):
        from tkinter_icons.iconset import get_icon_set
        from tkinter_icons.render import render_glyph

        note_self(self)
        static = figures_dir(self.env)
        lines = [".. container:: pack-comparison", ""]

        for extra in COMPARISON_PACKS:
            pack = pack_by_extra(extra)
            try:
                provider = provider_for(pack)
            except PackNotInstalled:
                not_installed(self, extra)
                continue
            style = provider.default_style
            icon_set = get_icon_set(provider, style)

            lines += ["   .. container:: comparison-row", ""]
            lines += ["      .. container:: comparison-label", "", f"         {pack.label}", ""]
            lines += ["      .. container:: comparison-glyphs", ""]

            for concept, by_pack in COMPARISON_ROWS:
                name = by_pack[extra]
                resolved = provider.resolve_icon_name(name, style)
                for theme, ink_color in INK.items():
                    image = render_glyph(
                        icon_set.glyph(resolved), COMPARISON_PX, ink_color,
                        font_key=icon_set.font_key, font_bytes=icon_set.font_bytes,
                        ink=icon_set.ink(resolved), options=icon_set.options,
                    )
                    if image.getchannel("A").getbbox() is None:
                        raise ValueError(
                            f"{extra}: {name!r} rendered nothing for the {concept!r} "
                            f"row. Fix COMPARISON_ROWS rather than shipping a gap."
                        )
                    stem = f"compare-{extra}-{concept}-{theme}"
                    save_atomic(image, static / f"{stem}.png")
                    lines += [
                        f"         .. image:: /_static/figures/{stem}.png",
                        f"            :alt: {pack.label} {concept}",
                        f"            :class: comparison-img only-{theme}",
                        "",
                    ]

        return self.parse_text_to_nodes("\n".join(lines))


def check_figures(app, env, docnames):
    """Every figure and comparison row names a pack that exists.

    A pack that is merely *uninstalled* degrades to a warning at render time,
    the way `pack_showcase` does. A pack that does not exist at all is a typo
    in this file, and the reader would otherwise meet it as a `KeyError` from
    inside a directive.
    """
    from tkinter_icons.packs import KNOWN_PACKS

    known = {pack.extra for pack in KNOWN_PACKS}

    for key, figure in FIGURES.items():
        if figure.pack not in known:
            logger.warning(
                "render_figures: FIGURES[%r] names pack %r, which does not exist",
                key, figure.pack, type="render_figures",
            )

    unknown = sorted(set(COMPARISON_PACKS) - known)
    if unknown:
        logger.warning(
            "render_figures: COMPARISON_PACKS names packs that do not exist: %s",
            ", ".join(unknown), type="render_figures",
        )

    # A missing entry would draw a short row, which reads as "this pack has no
    # star" rather than as a gap in this table.
    for concept, by_pack in COMPARISON_ROWS:
        missing = sorted(set(COMPARISON_PACKS) - set(by_pack))
        if missing:
            logger.warning(
                "render_figures: the %r row has no name for %s",
                concept, ", ".join(missing), type="render_figures",
            )


def setup(app):
    app.add_directive("renderer-figure", RendererFigureDirective)
    app.add_directive("pack-comparison", PackComparisonDirective)
    app.connect("env-before-read-docs", check_figures)
    # Safe for the same reasons `pack_showcase` is, and deliberately not for
    # the reason that module used to give. Read safety holds because nothing
    # here is mutated across workers: `FIGURES` and `COMPARISON_ROWS` are
    # read-only constants, and `check_figures` runs on `env-before-read-docs`,
    # which fires once in the parent.
    #
    # Write safety does *not* rest on each path having one writer. That
    # argument was true of `pack_showcase` until `icons-and-names` started
    # drawing Bootstrap's styles, and it failed silently — two workers, one
    # path, no warning. It is not worth re-deriving here for a module whose
    # figure keys happen to be unique today. Every write in both modules goes
    # through `save_atomic`, which writes beside the target and renames, so
    # colliding workers can only produce the same bytes and race the rename.
    # A new directive that writes an image must use it too.
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
