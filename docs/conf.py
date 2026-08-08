import importlib.metadata
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_ext"))

# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

project = "tkinter-icons"
author = "Israel Dryer"
copyright = f"2026, {author}"

release = importlib.metadata.version("tkinter-icons")
version = ".".join(release.split(".")[:2])

# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "sphinx_copybutton",
    "myst_parser",
    # Local: builds the icon-pack comparison table on packs.rst from the pack
    # catalog and the installed providers, so it cannot go stale. See
    # docs/_ext/packs_table.py.
    "packs_table",
    # Local: the card grid on packs.rst, and the facts table and preview strips
    # on each of the sixteen per-pack pages. The previews are drawn at build
    # time by this library, so the docs cannot claim a rendering the renderer
    # does not produce. See docs/_ext/pack_showcase.py.
    "pack_showcase",
    # Local: the side-by-side renders on the sizing page and the pack
    # comparison on choosing-a-pack. Same principle as pack_showcase, applied
    # to claims about the renderer rather than to the sets — a page that
    # asserts measured ink beats getbbox now shows both. See
    # docs/_ext/render_figures.py.
    "render_figures",
]

# The Release Notes page supplies its own reStructuredText H1 and includes the
# version entries from the root CHANGELOG.md, which begin at H2 - so myst's
# "headings start at H2, not H1" lint fires on that fragment by design. It is
# the only myst-parsed document, so silencing this one lint is precise.
suppress_warnings = ["myst.header"]

# ---------------------------------------------------------------------------
# Autodoc
# ---------------------------------------------------------------------------

autodoc_member_order = "groupwise"
autodoc_typehints = "description"
autodoc_typehints_format = "short"
# Only emit parameter type hints for params with an explicit docstring entry, so
# frozen dataclasses documented through attribute docstrings render each field
# once instead of also getting a description-less "Parameters" block synthesized
# from the generated __init__ signature. `RenderOptions` and `IconSet` are both
# that shape.
autodoc_typehints_description_target = "documented"
python_use_unqualified_type_names = True
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

# Single backticks render as inline code, matching the docstrings throughout the
# package - they were written for mkdocstrings, where that is the default.
default_role = "code"

# ---------------------------------------------------------------------------
# Napoleon (Google-style docstrings)
# ---------------------------------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_use_param = True
napoleon_use_rtype = False
napoleon_attr_annotations = True
# Render a class docstring's `Attributes:` section as `:ivar:` fields inside the
# class description, rather than as standalone `.. attribute::` directives.
# Without this, every documented attribute is described twice - once by napoleon
# from the docstring and once by autodoc from the class - and Sphinx reports each
# as a duplicate object description. `Icon`, `IconSet`, `RenderOptions`, and
# `Pack` all document their fields this way.
napoleon_use_ivar = True

# ---------------------------------------------------------------------------
# Intersphinx
# ---------------------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    # Pillow is part of this library's public surface, not an implementation
    # detail: `render_glyph` and `Icon.render_pil` hand back a `PIL.Image.Image`,
    # and `RenderOptions` is a description of how Pillow draws.
    "pillow": ("https://pillow.readthedocs.io/en/stable", None),
}

# ---------------------------------------------------------------------------
# Nitpicky cross-reference suppression
# ---------------------------------------------------------------------------
# Targets that are deliberately outside the documented API: Tk types (the point
# of the library is that you rarely name them), typing constructs, and private
# names. Keeps a `-n` build focused on links that are genuinely broken.

nitpick_ignore_regex = [
    (r"py:.*", r"typing\..*"),
    (r"py:.*", r"tkinter\..*"),
    (r"py:.*", r"PIL\..*"),
    (r"py:.*", r"(?:.*\.)?_[A-Za-z]\w*$"),
    # `Icon` inherits from `StatefulIconMixin`, so `:show-inheritance:` emits a
    # reference to it. The mixin itself is not part of the consumer API - the
    # methods it contributes, `map` and `unmap`, are documented on `Icon` via
    # `:inherited-members:`, which is where a reader looks for them.
    (r"py:class", r"tkinter_icons\.stateful_icon_mixin\..*"),
]

# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "github_url": "https://github.com/israel-dryer/tkinter-icons",
    # The project wordmark, copied from `assets/` - which is the source of truth
    # for every mark, and says so. `light`/`dark` name the **background** the
    # asset is drawn for, not its ink, so `wordmark-light` is dark ink for a
    # light page. Copies rather than references because `html_static_path` does
    # not reach outside the docs tree; update `assets/` first, then this copy.
    #
    # No `text` alongside them: these wordmarks already contain the lettering,
    # outlined to paths rather than live `<text>`, because an SVG used as a logo
    # loads as its own document and cannot see the page's `@font-face` rules.
    "logo": {
        "image_light": "_static/wordmark-light.svg",
        "image_dark": "_static/wordmark-dark.svg",
        "alt_text": "tkinter-icons",
    },
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "navbar_persistent": ["search-button"],
    "secondary_sidebar_items": ["page-toc"],
    "navigation_with_keys": True,
    "show_nav_level": 1,
    "icon_links": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/tkinter-icons/",
            "icon": "fa-brands fa-python",
        },
    ],
}

html_static_path = ["_static"]
templates_path = ["_templates"]
html_css_files = ["custom.css"]
html_favicon = "_static/favicon.png"
html_title = "tkinter-icons"
html_short_title = "tkinter-icons"
html_show_sourcelink = False
html_copy_source = False

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "requirements.txt"]