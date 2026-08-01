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

`SHOWCASE` is the one hand-maintained thing here, and it is checked: a name that
stops resolving raises during the build, which `-W` turns into a failure. It
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

#: Ink for each theme. `light`/`dark` name the background, matching the
#: convention `assets/README.md` sets for every other mark in the project.
INK = {"light": "#111827", "dark": "#F9FAFB"}

#: Representative names per pack, chosen to show what the set is like rather
#: than what it has in common with every other set. Where a pack's naming is
#: unusual the list says so by example: Fluent carries size and style in the
#: name, and Meteocons has no semantic names at all.
SHOWCASE: dict[str, list[str]] = {
    "bootstrap": ["house", "search", "gear", "person", "heart", "star", "download", "trash"],
    "devicon": ["python", "javascript", "react", "docker", "git", "linux", "rust", "go"],
    "eva": ["home", "search", "settings", "person", "heart", "star", "download", "trash"],
    "fluent": [
        "ic-fluent-home-24-regular", "ic-fluent-search-24-regular",
        "ic-fluent-settings-24-regular", "ic-fluent-person-24-regular",
        "ic-fluent-heart-24-regular", "ic-fluent-star-24-regular",
        "ic-fluent-mail-24-regular", "ic-fluent-alert-24-regular",
    ],
    "fluent-regular": [
        "ic-fluent-home-24-regular", "ic-fluent-search-24-regular",
        "ic-fluent-settings-24-regular", "ic-fluent-person-24-regular",
        "ic-fluent-heart-24-regular", "ic-fluent-star-24-regular",
        "ic-fluent-mail-24-regular", "ic-fluent-alert-24-regular",
    ],
    "fontawesome": ["house", "user", "heart", "star", "download", "trash", "calendar", "bell"],
    "google-material": ["home", "search", "settings", "person", "star", "download", "folder", "check"],
    "ionicons": ["home", "search", "settings", "heart", "star", "download", "trash", "person"],
    "lucide": ["house", "search", "settings", "user", "heart", "star", "download", "trash"],
    "material": ["home", "magnify", "cog", "account", "heart", "star", "download", "calendar"],
    "meteocons": ["sun", "moon", "cloud", "cloud-sun", "rain", "snow", "thunderstorm", "fog"],
    "remix": ["home", "search", "settings", "user", "heart", "star", "download", "delete-bin"],
    "rpg-awesome": [
        "broadsword", "crossed-swords", "shield", "potion",
        "dragon", "castle-flag", "helmet", "guarded-tower",
    ],
    "simple": ["github", "python", "docker", "rust", "linux", "firefox", "git", "npm"],
    "typicons": ["home", "cog", "user", "heart", "star", "download", "trash", "calendar"],
    "weather": ["day-sunny", "cloud", "rain", "snow", "thunderstorm", "fog", "windy", "night-clear"],
}


def pack_by_extra(extra: str):
    from tkinter_icons.packs import KNOWN_PACKS

    for pack in KNOWN_PACKS:
        if pack.extra == extra:
            return pack
    raise KeyError(f"no pack with extra {extra!r}")


def icon_class(pack):
    return getattr(importlib.import_module(pack.module), pack.icon_class)


def provider_for(pack):
    module = importlib.import_module(f"{pack.module}.provider")
    for name, obj in vars(module).items():
        if name.endswith("FontProvider") and name != "BaseFontProvider":
            return obj()
    raise LookupError(f"no provider class in {pack.module}.provider")


def render_strip(pack, names: list[str], style: str | None, ink: str, out: Path) -> None:
    """Compose one row of glyphs into a transparent PNG."""
    from PIL import Image

    from tkinter_icons.iconset import get_icon_set

    cls = icon_class(pack)
    provider = provider_for(pack)
    icon_set = get_icon_set(provider, style)

    width = len(names) * GLYPH_PX + (len(names) - 1) * GAP_PX
    strip = Image.new("RGBA", (width, GLYPH_PX), (0, 0, 0, 0))

    for index, name in enumerate(names):
        resolved = provider.resolve_icon_name(name, style)
        glyph = cls.render_pil(resolved, size=GLYPH_PX, color=ink, icon_set=icon_set)
        if glyph.getchannel("A").getbbox() is None:
            raise ValueError(
                f"{pack.extra}: {name!r} rendered nothing in style {style!r}. "
                f"Fix the name in SHOWCASE rather than shipping a blank preview."
            )
        strip.paste(glyph, (index * (GLYPH_PX + GAP_PX), 0), glyph)

    out.parent.mkdir(parents=True, exist_ok=True)
    strip.save(out)


class PackPreviewDirective(SphinxDirective):
    """Render this pack's showcase glyphs, one strip per style.

    Usage::

        .. pack-preview:: material
    """

    required_arguments = 1

    def run(self):
        extra = self.arguments[0]
        pack = pack_by_extra(extra)
        names = SHOWCASE[extra]
        provider = provider_for(pack)
        styles = list(provider.style_list) or [None]

        static = Path(self.env.app.srcdir) / "_static" / "previews"
        lines: list[str] = []

        for style in styles:
            for theme, ink in INK.items():
                filename = f"{extra}-{style or 'default'}-{theme}.png"
                render_strip(pack, names, style, ink, static / filename)

            if len(styles) > 1:
                lines += [f"``{style}``", ""]
            for theme in INK:
                lines += [
                    f".. image:: /_static/previews/{extra}-{style or 'default'}-{theme}.png",
                    f"   :alt: {pack.label} sample glyphs",
                    f"   :class: pack-preview pack-preview--{theme}",
                    "",
                ]

        shown = " · ".join(f"``{name}``" for name in names)
        lines += [shown, ""]
        return self.parse_text_to_nodes("\n".join(lines))


class PackFactsDirective(SphinxDirective):
    """The install line, import, styles, count, and links for one pack.

    Usage::

        .. pack-facts:: material
    """

    required_arguments = 1
    REPO = "https://github.com/israel-dryer/tkinter-icons/blob/main/packages"

    def run(self):
        extra = self.arguments[0]
        pack = pack_by_extra(extra)
        provider = provider_for(pack)
        index = provider.build_display_index()
        count = sum(len(v) for v in index["names_by_style"].values())
        styles = provider.style_list

        rows = [
            ("Install", f"``{pack.install_command}``"),
            ("Import", f"``{pack.import_statement}``"),
            ("Icons", f"{count:,}"),
            ("Styles", ", ".join(f"``{s}``" for s in styles) if styles else "none"),
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


def check_showcase(app, env, docnames):
    """Every pack has a showcase, and every showcase name belongs to a pack."""
    from tkinter_icons.packs import KNOWN_PACKS

    known = {pack.extra for pack in KNOWN_PACKS}
    missing = sorted(known - set(SHOWCASE))
    unknown = sorted(set(SHOWCASE) - known)
    if missing:
        logger.warning(
            "pack_showcase: no showcase icons for %s - add them to SHOWCASE",
            ", ".join(missing), type="pack_showcase",
        )
    if unknown:
        logger.warning(
            "pack_showcase: SHOWCASE names packs that do not exist: %s",
            ", ".join(unknown), type="pack_showcase",
        )


def setup(app):
    app.add_directive("pack-preview", PackPreviewDirective)
    app.add_directive("pack-facts", PackFactsDirective)
    app.connect("env-before-read-docs", check_showcase)
    return {"version": "1.0", "parallel_read_safe": False, "parallel_write_safe": True}
