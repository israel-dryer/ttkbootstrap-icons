Icons and names
===============

An icon is a description, not a picture
---------------------------------------

Creating an icon costs almost nothing. The constructor resolves the name, records the size and color, and stops — it does not open Tk, allocate an image, or touch a display:

.. code-block:: python

   from tkinter_icons import MaterialIcon

   home = MaterialIcon("home", size=24, color="#0F766E")   # nothing drawn yet
   home.image                                              # drawn here

That is why icons can be built before there is a root window, kept in a module-level table, or passed around as configuration. It is also why the same icon costs nothing twice: two icons with the same set, name, size, color, and options share one rendered image.

.. code-block:: python

   MaterialIcon("home", 24, "black").image is MaterialIcon("home", 24, "black").image
   # True - one image, cached per Tk interpreter

Naming
------

Names are the upstream project's own, lowercase and hyphenated:

.. code-block:: python

   MaterialIcon("account-circle")
   LucideIcon("chevron-right")
   BootstrapIcon("file-earmark-text")

If you are guessing, don't — run ``tkinter-icons`` and search. See :doc:`icon-browser`.

Styles
------

Some packs draw the same icon several ways. Bootstrap has ``outline`` and ``fill``; Font Awesome has ``solid``, ``regular``, and ``brands``; Google Material has four. A pack with styles takes a ``style`` argument, and you can also carry the style in the name:

.. code-block:: python

   from tkinter_icons import BootstrapIcon

   BootstrapIcon("house", style="fill")
   BootstrapIcon("house-fill")             # equivalent

When both are given and they disagree, that is an error rather than a silent preference:

.. code-block:: python

   BootstrapIcon("house-fill", style="outline")
   # ValueError: 'house-fill' is not valid for style 'outline' in bootstrap.
   #             Try style 'fill' or use an unsuffixed name.

The Styles column on :doc:`../packs` lists what each pack accepts; several packs have none and take no ``style`` argument at all.

.. _how-a-name-finds-its-style:

How a name finds its style
--------------------------

Three rules, tried in order. Every entry point uses them — the pack's constructor, :meth:`~tkinter_icons.Icon.render_pil`, and the browser — so a name means the same thing wherever you write it.

**An explicit** ``style`` **wins, and nothing else is consulted.** If the icon is not in that style you get a :class:`ValueError` rather than a quiet substitution from another one.

**Otherwise, a style written into the name wins.** ``"house-fill"`` is a request for the ``fill`` cut. It does not have to be at the end: Bootstrap names glyphs ``shield-fill-check`` and ``building-fill-add``, where the ``fill`` sits in the middle, and those are read the same way. What counts is a whole hyphen-separated piece of the name — never part of one, and never the first piece. Remix has a ``line`` style *and* a glyph called ``line-chart``, which is a chart rather than a line; Fluent's ``filled`` is not Bootstrap's ``fill``. Where two styles could both match, the longer one does, so Devicon's ``"aarch64-plain-wordmark"`` is a wordmark rather than a ``plain``.

**Otherwise the pack's default style is tried first, and the pack's other styles after it.** So ``BootstrapIcon("house")`` is the ``outline`` house, because Bootstrap draws a house both ways and ``outline`` is its default — but ``FontAwesomeIcon("accusoft")`` is a brand mark, because ``brands`` is the only style Font Awesome draws it in. The default settles which icon you get; it does not limit which icons you can ask for.

.. versionchanged:: 5.1.0
   The default style used to be the only place an unadorned name was looked for, so a name that existed *only* in some other style resolved nowhere. It is now a preference rather than a gate. Nothing that already resolved resolves differently: measured over every name of all sixteen packs, once with no style and once against each style its own pack has — 288,418 combinations — 849 names began resolving, none stopped, and none changed which glyph it gave.

   The default cannot simply be dropped, which is the obvious next thought. It is what settles the 13,658 names that exist in more than one style — ``MaterialIcon("home")``, ``EvaIcon("activity")`` — not one of which writes a style into the name, so each would otherwise be ambiguous and have to raise.

   Two functions used to read a style out of a name and read it differently, one matching anywhere in the name and the other only at the end, so which glyph you got could depend on the order a pack happened to declare its styles in. ``shield-fill-check`` was the visible cost: a real Bootstrap glyph its own constructor rejected.

A name that exists in several styles resolves to the default, so ``style`` is how you reach the others — and since packs are free to ship a glyph in one style only, it is also how you pin the one you meant rather than the one that happens to exist today.

A style is a different drawing of the same idea, not a different icon. Bootstrap's two, on the same six names:

.. pack-preview:: bootstrap

When a name is wrong
--------------------

Two different things can go wrong, and they are answered differently.

**A name the pack does not have raises**, from every entry point, the moment you ask:

.. code-block:: python

   MaterialIcon("hoome")
   # ValueError: hoome not found in lookup for mat in any of its styles: fill, outline.

   MaterialIcon.render_pil("hoome")
   # ValueError: hoome not found in lookup for mat in any of its styles: fill, outline.

The pack was asked for an icon it does not draw in any style. Nothing about that is recoverable, and a misspelling in an export script is worth stopping for — a transparent PNG written to disk looks like a success to every exit code that follows it.

.. versionchanged:: 5.1.0
   ``render_pil`` used to swallow this and return a transparent square, so the same typo raised one way and drew nothing the other. That was defensible while 849 real icons were also unreachable by name, because raising would have failed on names that were not typos at all. Both halves are fixed together: those names resolve now, so what is left really is a bad name.

**A name that reaches an icon set which cannot draw it applies a policy instead.** This is the other failure: the set's data is inconsistent with the names built from it, or you passed a glyph name straight to the base :class:`~tkinter_icons.Icon`, or to ``render_pil`` with an explicit ``icon_set``, neither of which resolves anything. That also raises by default, so both routes into the library answer a name they cannot draw the same way — but here it is a policy, and you can choose otherwise:

.. code-block:: python

   from tkinter_icons import Icon

   Icon.on_missing = "warn"      # or "transparent", or the default "raise"

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Value
     - Behavior
   * - ``"raise"``
     - Raise :class:`KeyError`. The default.
   * - ``"warn"``
     - Draw an empty square of the right size and emit a :class:`UserWarning`.
   * - ``"transparent"``
     - Draw the empty square and say nothing.

.. versionchanged:: 5.1.0
   The default was ``"transparent"``. A pack class had always raised :class:`ValueError` for a name it could not resolve, so the library answered one question two ways depending on which door you came in by — and the silent half was the one that wrote blank PNGs to disk. ``"transparent"`` is still there for callers who want it; it is now something you ask for.

``"warn"`` is what turns that blank square into something you can see without stopping the run, which suits a test suite or a bulk export: every bad name is reported and the run still finishes, rather than stopping at the first. Reach for it if you build icon sets yourself, or pass glyph names straight to :class:`~tkinter_icons.Icon`.

``"none"`` is not affected by any of this. It is the sentinel for *deliberately* no icon, so it draws a blank under every policy, including ``"raise"``.

**The mechanism now applies to a pack's own names too, and until 5.1.0 it could not.** Two things have to be true for an icon to draw: the name has to be in the pack's glyph map, and the glyph map's codepoint has to be in the pack's font. Only the first was ever checked. A name the map advertised at a codepoint the font had never carried resolved, looked up, and drew nothing at all — no exception, no warning, not even under ``"raise"``, because from the glyph map's point of view nothing was missing. No shipped pack is in that state now, and the rest of this section is about how it is kept that way.

.. versionchanged:: 5.1.0
   A codepoint the font does not contain is now the same kind of failure as a name the glyph map does not have, and ``on_missing`` governs both. The two are reported differently, because a user who mistyped and a user who hit a broken pack need different answers: the message for this case names the codepoint and says the fault is in the pack's data rather than in the name you asked for.

121 glyph-map entries were in that state when this was found: 119 across Google Material's ``outlined``, ``round`` and ``sharp`` cuts, and 2 in Material Design Icons. Counted the way the placement census counts — once per name *per style* — that is 123, because Material Design Icons' two styles are drawn from one font and share one glyph map. Both numbers are right; they measure different things, and quoting either without saying which is how a 123-glyph discrepancy once went unexplained for a whole review round.

The packs' generators were fixed too, so a regeneration cannot reintroduce them. Every pack now advertises exactly what it can draw, which ``tests/test_font_coverage.py`` asserts against every style of every installed pack.

Asking for a pack you have not installed
----------------------------------------

The import root knows all sixteen packs whether or not they are installed, so this fails with instructions rather than a bare :class:`ImportError` about a module you never named:

.. code-block:: python

   from tkinter_icons import WeatherIcon
   # ImportError: The Weather Icons pack is not installed.
   #
   #   pip install "tkinter-icons[weather]"
   #
   # Then: from tkinter_icons import WeatherIcon
   #
   # Currently installed: material, simple

Inspecting what you have
------------------------

The pack catalog is importable, which is useful in a diagnostics screen or a test that asserts what an environment carries:

.. code-block:: python

   from tkinter_icons import installed_packs, find_pack

   for pack in installed_packs():
       print(pack.extra, pack.label, pack.import_statement)

   find_pack("mat")                  # by provider name, extra, module, or distribution
   find_pack("tkinter-icons-mat")

What an icon knows about itself
-------------------------------

.. code-block:: python

   icon = MaterialIcon("home", size=15)

   icon.name             # 'home' - the resolved glyph name
   icon.size             # 15 - what you asked for
   icon.rendered_size    # 16 - what was drawn; odd sizes snap up
   icon.icon_set         # the IconSet it draws from
   icon.icon_set.id      # 'mat:default'
   len(icon.icon_set)    # how many glyphs that set has
   "home" in icon.icon_set

:attr:`~tkinter_icons.Icon.rendered_size` is worth knowing if you are laying out around an icon — see :doc:`sizing-and-quality`.