"""Every icon a documentation example names has to be one the pack ships.

The docs teach by example, and an example that raises teaches nothing — it is
also the one kind of documentation bug a reader hits *before* they read the
prose around it. `sphinx -W` does not run code blocks, so a page can build
cleanly while its centerpiece example is impossible.

It happened: the block introducing `style=` on `render_pil` in
`docs/user-guide/headless-rendering.rst` called
`FontAwesomeIcon.render_pil("house", style="regular")`. Font Awesome Free's
`regular` cut has 422 names and `house` is not among them — it exists only in
`solid` — so the example demonstrating the feature the release adds raised
`ValueError` for every reader who copied it.

The blocks are parsed with `ast` rather than scanned with a regex. A regex over
prose that matches nothing looks exactly like a regex over prose that finds no
problems, which is how the American-spelling sweep silently skipped `.github/`;
`test_the_examples_are_actually_being_found` is the floor that makes a silent
zero fail.

Scope is deliberately narrow: a call whose icon name *and* style are string
literals, on a pack class that is installed. Anything built from a variable, a
loop, or an f-string is left alone — resolving those means running the block,
and two of the headless examples write files into the current directory.
"""

from __future__ import annotations

import ast
import importlib
import textwrap
from pathlib import Path

import pytest

from tkinter_icons.packs import KNOWN_PACKS

DOCS = Path(__file__).resolve().parents[1] / "docs"

INSTALLED = {pack.icon_class: pack for pack in KNOWN_PACKS if pack.is_installed}
for _pack in list(KNOWN_PACKS):
    if _pack.is_installed and _pack.alias:
        INSTALLED.setdefault(_pack.alias, _pack)


def python_blocks(path):
    """Yield the source of every `.. code-block:: python` in an rst file.

    Indentation-based, matching how docutils delimits a directive body: the
    block is every line indented past the directive, and it ends at the first
    non-blank line that is not.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped in (".. code-block:: python", ".. code-block:: python3"):
            indent = len(lines[i]) - len(lines[i].lstrip())
            i += 1
            body = []
            while i < len(lines):
                line = lines[i]
                if not line.strip():
                    body.append("")
                    i += 1
                    continue
                if len(line) - len(line.lstrip()) <= indent:
                    break
                body.append(line)
                i += 1
            # Drop directive options (`:emphasize-lines:` and friends) and
            # dedent to column zero so `ast` will accept it.
            body = [ln for ln in body if not ln.strip().startswith(":")]
            text = "\n".join(body)
            if text.strip():
                yield textwrap.dedent(text)
        else:
            i += 1


def literal_icon_calls(source):
    """Every `(class, name, style)` a block names entirely in string literals.

    Matches both spellings the docs use — `PackIcon("name", style=...)` and
    `PackIcon.render_pil("name", style=...)` — and skips anything whose name is
    not a plain string, or that passes `icon_set=`, which resolves against the
    set instead of the provider.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        # A fragment continuing an earlier block on the same page.
        return

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "render_pil":
            owner = func.value
        elif isinstance(func, ast.Name):
            owner = func
        else:
            continue

        if not isinstance(owner, ast.Name) or owner.id not in INSTALLED:
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        name = node.args[0].value
        if not isinstance(name, str):
            continue

        keywords = {kw.arg: kw.value for kw in node.keywords}
        if "icon_set" in keywords:
            continue
        style_node = keywords.get("style")
        if style_node is None:
            style = None
        elif isinstance(style_node, ast.Constant) and isinstance(style_node.value, str):
            style = style_node.value
        else:
            continue

        yield owner.id, name, style


def collect():
    found = []
    for path in sorted(DOCS.rglob("*.rst")):
        if "_build" in path.parts:
            continue
        for block in python_blocks(path):
            for class_name, name, style in literal_icon_calls(block):
                found.append((path, class_name, name, style))
    return found


EXAMPLES = collect()

#: Names a page shows *failing* on purpose, as `# ValueError: ...`. Each is
#: checked to raise rather than merely skipped, so a page cannot keep teaching
#: a failure the library stopped producing.
DELIBERATE_FAILURES = {
    ("FontAwesomeIcon", "accusoft", "solid"),
    ("BootstrapIcon", "house-fill", "outline"),
    ("MaterialIcon", "hoome", None),
}


def provider_for(pack):
    module = importlib.import_module(f"{pack.module}.provider")
    for name, obj in vars(module).items():
        if name.endswith("FontProvider") and name != "BaseFontProvider":
            return obj()
    raise LookupError(f"no provider class in {pack.module}.provider")


def test_the_examples_are_actually_being_found():
    """The floor. A parser that matches nothing passes every test below it."""
    assert len(EXAMPLES) >= 20, (
        f"only {len(EXAMPLES)} literal icon call(s) found across the docs — the block "
        f"parser has probably stopped matching, which would make the checks below vacuous"
    )
    pages = {path.name for path, *_ in EXAMPLES}
    assert "headless-rendering.rst" in pages
    assert "icons-and-names.rst" in pages


def test_no_deliberate_failure_has_gone_stale():
    """An exemption for an example that no longer exists exempts nothing.

    Without this, deleting the block that shows `MaterialIcon("hoome")` leaves
    a permanent entry excusing a name nobody shows any more — and the next
    person to add that name for real inherits the exemption.
    """
    shown = {(class_name, name, style) for _path, class_name, name, style in EXAMPLES}
    stale = DELIBERATE_FAILURES - shown
    assert not stale, f"no docs example shows {stale}; drop the exemption"


@pytest.mark.parametrize(
    "path,class_name,name,style",
    EXAMPLES,
    ids=[f"{p.stem}:{c}:{n}:{s}" for p, c, n, s in EXAMPLES],
)
def test_every_name_a_docs_example_shows_resolves(path, class_name, name, style):
    pack = INSTALLED[class_name]
    provider = provider_for(pack)
    key = (class_name, name, style)

    if key in DELIBERATE_FAILURES:
        with pytest.raises(ValueError):
            provider.resolve_icon(name, style)
        return

    try:
        provider.resolve_icon(name, style)
    except ValueError as exc:
        rel = path.relative_to(DOCS.parent)
        pytest.fail(
            f"{rel} shows `{class_name}(\"{name}\""
            + (f", style=\"{style}\"" if style else "")
            + f")`, which raises: {exc}"
        )
