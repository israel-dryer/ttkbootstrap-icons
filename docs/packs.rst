Icon packs
==========

``tkinter-icons`` ships no glyphs. It is the renderer; the icons come from one of sixteen packs, each installed as an extra:

.. code-block:: bash

   pip install "tkinter-icons[material]"

.. code-block:: python

   from tkinter_icons import MaterialIcon

Each pack is its own PyPI distribution because each carries its own font file, but you should never have to think about that. Install the extra, import from ``tkinter_icons``, and the pack's name is an implementation detail.

The sixteen sets
----------------

Each card carries a sample of the set, the extra that installs it, and roughly how many icons it has. Open one for the same glyphs drawn in every style the pack offers, a runnable example, and the exact figures.

.. pack-cards::

Side by side
------------

**Install** is the extra to add to ``pip install "tkinter-icons[...]"``. **Icons** counts distinct names across all of that pack's styles.

.. packs-table::

.. note::

   Counts, styles, and the previews above are read from the installed packs when the documentation is built, not typed in — so they describe exactly the release you are reading about.

:doc:`getting-started/choosing-a-pack` is the shorter answer if you would rather be told than compare.

Using two at once
-----------------

Nothing stops you. Name both extras, import both classes, and they coexist — each icon holds its own icon set, so the two never interfere.

.. code-block:: bash

   pip install "tkinter-icons[lucide,simple]"

.. code-block:: python

   from tkinter_icons import LucideIcon, SimpleIcon

   save = LucideIcon("save", size=20)
   github = SimpleIcon("github", size=20)

The usual reason is a UI set plus a logo set: no general-purpose pack has a GitHub mark, and no logo pack has a "save" icon.

.. warning::

   There is deliberately no ``[all]`` extra. The sets serve disjoint purposes, so no application draws from all sixteen, and installing every one costs about 22 MB on disk to get fifteen sets nobody opens — the bundling that extras exist to avoid. Name the ones you use.

Styles
------

Some packs draw the same icon more than one way — outline and fill, solid and regular. Those are **styles**, and a pack that has them takes a ``style`` argument:

.. code-block:: python

   from tkinter_icons import BootstrapIcon

   BootstrapIcon("house", style="outline")
   BootstrapIcon("house", style="fill")
   BootstrapIcon("house-fill")            # same thing, style carried in the name

Of the :packs-stat:`total`, :packs-stat:`unstyled` have no styles at all and take no ``style`` argument. The Styles column above lists what each pack accepts, each pack's own page marks its default, and :doc:`user-guide/icons-and-names` covers how a name resolves against a style.

Upstream sources
----------------

Every pack redistributes someone else's icon font under its own license, and ships that license inside the installed package. Drawing the glyphs in your application is what these licenses are for, but a few carry attribution terms — see `THIRD-PARTY-NOTICES.md <https://github.com/israel-dryer/tkinter-icons/blob/main/THIRD-PARTY-NOTICES.md>`__ for the details per pack, or a pack's own page for its upstream project and license.

Nothing installed yet?
----------------------

If you got here from an error message, this is what it was telling you: the base package is a renderer, and it needs a pack before it can draw. Pick one from the grid above and install it as an extra. Anything from the list works with the same code.

.. code-block:: bash

   pip install "tkinter-icons[bootstrap]"     # Bootstrap Icons
   pip install "tkinter-icons[fontawesome]"   # Font Awesome 6 Free
   pip install "tkinter-icons[material]"      # Material Design Icons

.. toctree::
   :hidden:
   :maxdepth: 1

   packs/bootstrap
   packs/devicon
   packs/eva
   packs/fluent
   packs/fluent-regular
   packs/fontawesome
   packs/google-material
   packs/ionicons
   packs/lucide
   packs/material
   packs/meteocons
   packs/remix
   packs/rpg-awesome
   packs/simple
   packs/typicons
   packs/weather