"""The icon-pack comparison table, built from the catalogue rather than typed out.

The sixteen packs differ from each other only in data — class name, extra, style
list, upstream version, glyph count — which is why they get one page and one
table instead of sixteen near-identical pages. That reasoning only holds if the
table is *right*, and a hand-maintained one drifts: sixteen copies of the same
install line all went stale at once under the old docs, which is what retired
them.

So the numbers come from where they already live. `KNOWN_PACKS` is the single
source of truth for what a pack is called and how it is installed; the provider
itself knows its styles, upstream version, and homepage; and the glyph count is
the length of the glyph map it ships. Nothing here is transcribed.

That means a docs build needs the packs installed. A pack that is missing is
reported as a Sphinx warning and rendered with an em dash in the columns it
cannot fill — so a local build without the packs still works and still reads
correctly, while the docs workflow (which builds with `-W`) refuses to publish a
table with holes in it.
"""

from __future__ import annotations

from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

logger = logging.getLogger(__name__)

#: Rendered when a pack is not importable, so a hole is visible rather than
#: reading as a real (and wrong) answer such as "0 icons" or "no styles".
UNKNOWN = "—"


def _provider_for(pack):
    """Return an instantiated provider for `pack`, or None if it is not installed."""
    import importlib

    module = importlib.import_module(f"{pack.module}.provider")
    for name, obj in vars(module).items():
        if name.endswith("FontProvider") and name != "BaseFontProvider":
            return obj()
    raise LookupError(f"no provider class found in {pack.module}.provider")


def _glyph_count(provider) -> int:
    """Total distinct icon names across the provider's styles."""
    index = provider.build_display_index()
    return sum(len(names) for names in index["names_by_style"].values())


#: Built once per build. Both directives on the packs page need the same data,
#: and gathering it means instantiating sixteen providers and building sixteen
#: name lookups — worth doing once. Without the cache the "not installed"
#: warning also fired once per directive, so a missing pack was reported twice.
_ROWS_CACHE: list | None = None


def _pack_rows():
    """Return one row of table data per known pack, in catalogue order."""
    global _ROWS_CACHE
    if _ROWS_CACHE is None:
        _ROWS_CACHE = list(_build_pack_rows())
    return _ROWS_CACHE


def _build_pack_rows():
    """Yield the rows, reading each pack's provider once."""
    from tkinter_icons.packs import KNOWN_PACKS

    missing = []
    for pack in KNOWN_PACKS:
        row = {
            "pack": pack,
            "styles": UNKNOWN,
            "icons": UNKNOWN,
            "version": UNKNOWN,
            "homepage": None,
            "license_url": None,
        }
        try:
            provider = _provider_for(pack)
        except Exception:
            missing.append(pack.extra)
            yield row
            continue

        styles = provider.style_list
        # "none" rather than the em dash: a pack with no styles is answering the
        # question, where the dash means the pack could not be read at all.
        row["styles"] = ", ".join(f"``{s}``" for s in styles) if styles else "none"
        row["icons"] = f"{_glyph_count(provider):,}"
        row["version"] = provider.icon_version or UNKNOWN
        row["homepage"] = provider.homepage
        row["license_url"] = provider.license_url
        yield row

    if missing:
        logger.warning(
            "packs-table: %d pack(s) not installed, so their columns are blank: %s. "
            "Install them before building the published docs: "
            "pip install -e packages/tkinter-icons-<pack>",
            len(missing),
            ", ".join(missing),
            type="packs_table",
        )


def _cell(text: str) -> str:
    """Escape a cell so a stray pipe cannot break the list-table markup."""
    return text.replace("|", r"\|")


class PacksTableDirective(SphinxDirective):
    """Render the pack catalogue as a comparison table.

    Usage::

        .. packs-table::
    """

    has_content = False

    def run(self):
        lines = [
            ".. list-table::",
            "   :header-rows: 1",
            "   :widths: 22 20 20 18 10 10",
            "   :class: packs-table",
            "",
            "   * - Icon set",
            "     - Install",
            "     - Import",
            "     - Styles",
            "     - Icons",
            "     - Version",
        ]

        for row in _pack_rows():
            pack = row["pack"]
            if row["homepage"]:
                name = f"`{pack.label} <{row['homepage']}>`__"
            else:
                name = pack.label
            lines += [
                f"   * - {_cell(name)}",
                f"     - ``[{pack.extra}]``",
                f"     - ``{pack.alias}``",
                f"     - {_cell(row['styles'])}",
                f"     - {row['icons']}",
                f"     - {row['version']}",
            ]

        return self.parse_text_to_nodes("\n".join(lines))


class PackLinksDirective(SphinxDirective):
    """Render per-pack upstream and changelog links as a definition list.

    Kept out of the comparison table on purpose: three URLs per row makes the
    table unreadable at any width, and these are followed one at a time rather
    than compared across packs.
    """

    has_content = False

    REPO = "https://github.com/israel-dryer/tkinter-icons/blob/main/packages"

    def run(self):
        lines = []
        for row in _pack_rows():
            pack = row["pack"]
            links = []
            if row["homepage"]:
                links.append(f"`browse the set <{row['homepage']}>`__")
            if row["license_url"]:
                links.append(f"`upstream license <{row['license_url']}>`__")
            links.append(f"`changelog <{self.REPO}/{pack.distribution}/CHANGELOG.md>`__")
            lines += [f"{pack.label}", f"   {' · '.join(links)}", ""]

        return self.parse_text_to_nodes("\n".join(lines))


def setup(app):
    app.add_directive("packs-table", PacksTableDirective)
    app.add_directive("pack-links", PackLinksDirective)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}