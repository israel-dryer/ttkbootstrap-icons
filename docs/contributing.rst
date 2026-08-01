Contributing
============

This page covers working *on* the library rather than with it: the repository layout, the developer API that packs are built against, and how a new pack is made.

The repository
--------------

Eighteen distributions live in one repository — the base package, sixteen icon packs, and a compatibility shim:

.. code-block:: text

   packages/
     tkinter-icons/              the renderer, the browser, the pack catalogue
     tkinter-icons-bs/           one directory per pack ...
     tkinter-icons-mat/
     ...
     ttkbootstrap-icons-shim/    builds the `ttkbootstrap-icons` distribution
   tests/                        one suite, covering all of them
   docs/                         this documentation

The shim's directory is deliberately not named after the distribution it builds: the plain name belonged to the package being renamed away from. Anything mapping tags to directories has to go through ``.github/scripts/packages.py``, which reads every ``pyproject.toml`` rather than assuming ``packages/<dist>``.

Setting up
----------

.. code-block:: bash

   python -m venv .venv
   .venv/Scripts/python -m pip install -e packages/tkinter-icons
   .venv/Scripts/python -m pip install --no-deps -e packages/tkinter-icons-bs
   .venv/Scripts/python -m pip install -r docs/requirements.txt
   .venv/Scripts/python -m pytest -q

.. important::

   ``--no-deps`` on the packs is not optional in a working tree. Every pack requires ``tkinter-icons>=5.0.0``, and the base package's version comes from ``git describe`` — so before a ``v5.0.0`` tag exists it reports something like ``4.0.1.dev32+g4f9beca``, which is *below* the floor. Without ``--no-deps``, pip decides your local base package will not do and fetches one from PyPI. Their only other dependency is Pillow, which the base install already brought in.

   The alternative is to tell setuptools-scm what to claim: ``SETUPTOOLS_SCM_PRETEND_VERSION_FOR_TKINTER_ICONS=5.0.0``.

Install every pack when you are working on the packs themselves, on the packs page of these docs, or on anything that measures glyphs:

.. code-block:: bash

   .venv/Scripts/python -m pip install --no-deps $(printf -- '-e %s ' packages/tkinter-icons-*/)

Tests
-----

.. code-block:: bash

   python -m pytest -q

Most of the suite renders through :meth:`Icon.render_pil <tkinter_icons.Icon.render_pil>`, which is pure Pillow and needs no display. The Tk-level tests skip themselves where there is no display; on Linux CI they run under ``xvfb-run``.

.. note::

   Tk 8.6 cannot reliably create a second interpreter in one process — reloading ttk themes intermittently fails. Tests needing a fresh root guard themselves with ``pytest.skip`` on ``TclError``, and *which* test trips it depends on ordering, so a run reporting one skip and a run reporting none are both correct. This is a Tk limitation, not a bug to fix here.

Building the docs
-----------------

.. code-block:: bash

   python -m sphinx docs docs/_build/html -b html -W -n

The packs page reads each pack's styles, upstream version, and glyph count from the installed provider rather than from a table someone has to remember to update, so a build without the packs installed leaves those columns blank and warns. ``-W`` turns that into a failure, which is what the docs workflow uses — a published table with holes in it would be worse than none. ``-n`` does the same for unresolved cross-references, so a renamed API leaves a failing build rather than a dead link.

Deploying needs the repository's Pages source set to **GitHub Actions** rather than to a branch. The site was published by hand with ``mkdocs gh-deploy`` before this, which left a ``gh-pages`` branch; while Pages is still pointed at that branch, the deploy job fails.

The developer API
-----------------

An icon pack is a distribution that ships a font, a glyph map, measured metrics, and a provider class registered on an entry point. These are the pieces it is built from.

.. currentmodule:: tkinter_icons.providers

.. autoclass:: BaseFontProvider
   :members:
   :member-order: groupwise

.. currentmodule:: tkinter_icons.registry

.. autoclass:: ProviderRegistry
   :members:

.. autofunction:: load_external_providers

.. autodata:: PROVIDER_GROUP

.. autodata:: LEGACY_PROVIDER_GROUP

.. note::

   Both entry-point groups are scanned, and that is deliberate. Dropping the pre-rename group would mean anyone upgrading the base package with an old ``ttkbootstrap-icons-*`` pack installed silently loses every icon set.

Building a pack
---------------

A pack is roughly a hundred lines, most of it data. Copy the closest existing one — the packs are near-identical by design.

**1. The provider** describes the set to the renderer:

.. code-block:: python

   from tkinter_icons.providers import BaseFontProvider


   class ExampleFontProvider(BaseFontProvider):
       def __init__(self):
           super().__init__(
               name="example",
               display_name="Example Icons",
               package="tkinter_icons_example",
               filename="fonts/example.ttf",
               homepage="https://example.com/icons",
               license_url="https://example.com/icons/LICENSE",
               icon_version="1.0.0",
               pad_factor=0.10,
           )

Styles are a mapping when a set has them, each naming a font file, a predicate on the glyph name, or both:

.. code-block:: python

   styles={
       "outline": {"filename": "fonts/example.ttf", "predicate": lambda n: not n.endswith("-fill")},
       "fill": {"filename": "fonts/example.ttf", "predicate": lambda n: n.endswith("-fill")},
   },
   default_style="outline",

**2. The icon class** resolves names and hands off:

.. code-block:: python

   from tkinter_icons.icon import Icon

   from tkinter_icons_example.provider import ExampleFontProvider


   class ExampleIcon(Icon):
       def __init__(self, name, size=24, color="black", style=None):
           provider = ExampleFontProvider()
           ExampleIcon.initialize_with_provider(provider)
           super().__init__(provider.resolve_icon_name(name, style), size, color)

**3. The glyph map**, ``glyphmap.json`` beside the font — or ``glyphmap-<style>.json`` per style when the styles use different fonts. Three shapes are accepted, since the packs grew up separately:

.. code-block:: json

   {"house": "EA01"}
   {"house": {"unicode": "EA01"}}
   [{"name": "house", "unicode": "EA01"}]

**4. The entry point**, in the pack's ``pyproject.toml``:

.. code-block:: toml

   [project.entry-points."tkinter_icons.providers"]
   example = "tkinter_icons_example.provider:ExampleFontProvider"

.. warning::

   The registry registers a provider under ``provider.name``, **not** under the entry-point key. They match for every pack but one — the ``fa`` entry point registers ``fontawesome`` — so anything passing a pack name to a tool has to import the provider to get it. Reading the key gives an argument ``generate_metrics`` rejects.

**5. The metrics.** Measure the glyph ink, or the renderer falls back to ``getbbox`` and your icons sit slightly wrong:

.. code-block:: bash

   python -m tkinter_icons.tools.generate_metrics example

**6. The catalogue.** Add a :class:`~tkinter_icons.Pack` entry to ``KNOWN_PACKS`` in ``packs.py`` and an extra to the base package's ``pyproject.toml``. That is what makes ``pip install "tkinter-icons[example]"`` and ``from tkinter_icons import ExampleIcon`` work, and what every install message reads from.

**7. The PyInstaller hook**, one file in ``tkinter_icons/_pyinstaller/``:

.. code-block:: python

   from PyInstaller.utils.hooks import collect_data_files

   datas = collect_data_files('tkinter_icons_example')

Without it, a frozen application ships without your font and draws nothing — silently, since a missing glyph renders transparent. The test suite checks every pack in the catalogue has one.

**8. The upstream license**, verbatim, under ``LICENSES/`` in the pack. The preflight fails without it.

Maintainer tools
----------------

These regenerate assets into a *source tree*, so they do nothing from an installed wheel and deliberately ship in none of them. Run them with ``python -m`` from a checkout:

.. code-block:: bash

   python -m tkinter_icons.tools.generate_metrics --all      # measure every installed pack
   python -m tkinter_icons.tools.generate_metrics --check    # verify without writing
   python -m tkinter_icons.tools.build_all                   # rebuild pack assets from upstream

   python .github/scripts/verify_packages.py                 # packaging preflight
   python .github/scripts/verify_packages.py --strict        # what the release runs

``verify_packages.py`` asks one question of every distribution: *would this still work if the only thing that existed were the built distribution?* Package-data globs that match nothing, license files that are declared but absent, metrics that exist on disk but outside the glob that ships them — none of those are visible in a working tree, where the files are simply there.

Pull requests
-------------

Branch from ``5.0`` while 5.0.0 is in flight, and target it. Name the issue the change closes; the whole branch merges to ``main`` once, at release, which is when those issues close.

Releasing is tag-driven through Trusted Publishing, and publish order is load-bearing — the packs first, then the base package, then the shim. ``RELEASE.md`` has the details.