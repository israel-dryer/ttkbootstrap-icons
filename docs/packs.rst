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

**Install** is the extra to add to ``pip install "tkinter-icons[...]"``. **Import** is the class name, from ``tkinter_icons``. **Icons** counts distinct names across all of that pack's styles.

.. packs-table::

.. note::

   Counts and versions on this page are read from the installed packs when the documentation is built, not typed in — so they describe exactly the release you are reading about.

Choosing one
------------

The sets overlap far less than their sizes suggest. Four questions usually settle it.

**Do you need a general-purpose UI set?** ``[material]`` is the largest by a wide margin and covers almost anything an application needs. ``[lucide]`` is smaller, lighter in weight, and consistent. ``[bootstrap]`` is a good middle ground with a fill/outline pair for most icons. ``[remix]``, ``[eva]``, ``[ionicons]``, and ``[typicons]`` are alternatives in the same space with their own drawing style.

**Do you need Font Awesome specifically?** ``[fontawesome]`` is the one people usually mean by name, and it brings three styles — ``solid``, ``regular``, and ``brands`` — in one pack.

**Do you need logos?** ``[simple]`` carries several thousand brand marks; ``[devicon]`` carries developer tooling and language logos. Neither is a UI set — they have no "save" or "settings" icon — so you will usually pair one with a general-purpose pack.

**Do you need something specialised?** ``[weather]`` and ``[meteocons]`` draw forecast symbols; ``[rpg-awesome]`` draws swords, potions, and monsters; ``[google-material]`` is Google's own set in four styles, distinct from ``[material]`` (which is the community-extended Pictogrammers set).

Using two at once
-----------------

Nothing stops you. Name both extras, import both classes, and they coexist — each icon holds its own icon set, so the two never interfere.

.. code-block:: bash

   pip install "tkinter-icons[lucide,simple]"

.. code-block:: python

   from tkinter_icons import LucideIcon, SimpleIcon

   save = LucideIcon("save", size=20)
   github = SimpleIcon("github", size=20)

.. warning::

   There is deliberately no ``[all]`` extra. The sets serve disjoint purposes, so no application draws from all sixteen, and installing every one costs about 17 MB to get fifteen sets nobody opens — the bundling that extras exist to avoid. Name the ones you use.

Styles
------

Some packs draw the same icon more than one way — outline and fill, solid and regular. Those are **styles**, and a pack that has them takes a ``style`` argument:

.. code-block:: python

   from tkinter_icons import BootstrapIcon

   BootstrapIcon("house", style="outline")
   BootstrapIcon("house", style="fill")
   BootstrapIcon("house-fill")            # same thing, style carried in the name

Seven of the sixteen have no styles at all and take no ``style`` argument. The Styles column above lists what each pack accepts, and :doc:`user-guide/icons-and-names` covers how a name resolves against a style.

Upstream sources
----------------

Every pack redistributes someone else's icon font under its own license, and ships that license inside the installed package. Drawing the glyphs in your application is what these licenses are for, but a few carry attribution terms — see `THIRD-PARTY-NOTICES.md <https://github.com/israel-dryer/tkinter-icons/blob/main/THIRD-PARTY-NOTICES.md>`__ for the details per pack.

.. pack-links::

Nothing installed yet?
----------------------

If you got here from an error message, this is what it was telling you: the base package is a renderer, and it needs a pack before it can draw. Pick one from the table above and install it as an extra. Anything from the list works with the same code.

.. code-block:: bash

   pip install "tkinter-icons[bootstrap]"     # Bootstrap Icons
   pip install "tkinter-icons[fontawesome]"   # Font Awesome 6 Free
   pip install "tkinter-icons[material]"      # Material Design Icons