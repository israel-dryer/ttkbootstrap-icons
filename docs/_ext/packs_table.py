"""The icon-pack comparison table, built from the catalogue rather than typed out.

A hand-maintained table drifts: sixteen copies of the same install line all went
stale at once under the old docs, which is what retired them. So the numbers come
from where they already live. `KNOWN_PACKS` is the single source of truth for what
a pack is called and how it is installed; the provider itself knows its styles and
its glyph count. Nothing here is transcribed.

The table is deliberately narrow. It answers *which pack* — the four columns you
scan down when comparing — and hands off to `docs/packs/<extra>` for everything
you read once you have chosen: the import line, the upstream version, the links,
and what the set actually looks like. Those live in `pack_showcase`, and the set
name in the first column is the link to them.

That means a docs build needs the packs installed. A pack that is missing is
reported as a Sphinx warning and rendered with an em dash in the columns it
cannot fill — so a local build without the packs still works and still reads
correctly, while the docs workflow (which builds with `-W`) refuses to publish a
table with holes in it.
"""

from __future__ import annotations

from docutils import nodes
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


#: Built once per build. The table and the counted statistics need the same
#: data, and gathering it means instantiating sixteen providers and building
#: sixteen name lookups — worth doing once. Without the cache the "not
#: installed" warning also fired once per caller, so a missing pack was
#: reported several times over.
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
        row = {"pack": pack, "styles": UNKNOWN, "icons": UNKNOWN, "count": 0}
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
        row["count"] = _glyph_count(provider)
        row["icons"] = f"{row['count']:,}"
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
        # Sphinx invalidates a document when the document or `conf.py` changes,
        # not when an extension does — so without this, editing the columns
        # below leaves the old table in place and the build reports success.
        self.env.note_dependency(__file__)
        lines = [
            ".. list-table::",
            "   :header-rows: 1",
            "   :widths: 34 24 28 14",
            "   :class: packs-table",
            "",
            "   * - Icon set",
            "     - Install",
            "     - Styles",
            "     - Icons",
        ]

        for row in _pack_rows():
            pack = row["pack"]
            lines += [
                f"   * - :doc:`{_cell(pack.label)} <packs/{pack.extra}>`",
                f"     - ``[{pack.extra}]``",
                f"     - {_cell(row['styles'])}",
                f"     - {row['icons']}",
            ]

        return self.parse_text_to_nodes("\n".join(lines))


#: Small counts read better spelled out mid-sentence than as digits, and every
#: number this produces is bounded by the number of packs.
_WORDS = (
    "no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty",
)


def _spell(n: int) -> str:
    return _WORDS[n] if n < len(_WORDS) else str(n)


#: The counted facts the prose is allowed to state. Each takes the table rows.
#:
#: `icons` is rounded down to a round thousand rather than given exactly. The
#: landing page uses it as a headline, where "61,000+" is read as a magnitude
#: and "61,153" is read as a number someone will check — and it would change
#: every time a pack tracks an upstream release. The exact figure is a column
#: of the table on the packs page, which is where a reader who wants it looks.
_STATS = {
    "total": lambda rows: _spell(len(rows)),
    "styled": lambda rows: _spell(sum(1 for r in rows if r["styles"] not in ("none", UNKNOWN))),
    "unstyled": lambda rows: _spell(sum(1 for r in rows if r["styles"] == "none")),
    "icons": lambda rows: f"{sum(r['count'] for r in rows) // 1000:,},000+",
}


def packs_stat_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """One counted fact about the catalogue, inline in a sentence.

    Usage::

        The other :packs-stat:`unstyled` take no ``style`` argument.

    Exists because "seven of the sixteen have no styles" was typed into the
    prose while the same number was being generated three inches above it, in
    the table. Anything that is counted should be counted.
    """
    inliner.document.settings.env.note_dependency(__file__)
    if text not in _STATS:
        message = inliner.reporter.error(
            f"unknown pack statistic {text!r}; known: {', '.join(_STATS)}",
            line=lineno,
        )
        return [inliner.problematic(rawtext, rawtext, message)], [message]
    return [nodes.Text(_STATS[text](_pack_rows()))], []


def setup(app):
    app.add_directive("packs-table", PacksTableDirective)
    app.add_role("packs-stat", packs_stat_role)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}