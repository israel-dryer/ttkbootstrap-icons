Choosing a pack
===============

:doc:`../packs` lists all sixteen with their exact sizes, styles, and upstream versions. This page is the shorter answer.

You are not locked in either way. Every pack's icon class takes the same arguments, so trying another set is an install and a one-line change:

.. code-block:: python

   # from tkinter_icons import MaterialIcon as Icon
   from tkinter_icons import LucideIcon as Icon

Start here
----------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: A general-purpose UI set

      ``[material]`` is the largest by a wide margin and has an icon for almost anything. ``[lucide]`` is smaller, lighter in weight, and very consistent. ``[bootstrap]`` sits in between, with an outline/fill pair for most icons.

   .. grid-item-card:: Font Awesome

      ``[fontawesome]`` is the one people usually mean by name, and brings three styles — ``solid``, ``regular``, and ``brands`` — in a single pack.

   .. grid-item-card:: Logos and brand marks

      ``[simple]`` carries several thousand company marks; ``[devicon]`` carries language and developer-tooling logos. Neither is a UI set, so pair one with a general-purpose pack.

   .. grid-item-card:: Something specialised

      ``[weather]`` and ``[meteocons]`` draw forecast symbols. ``[rpg-awesome]`` draws swords, potions, and monsters.

What actually distinguishes them
--------------------------------

**Size.** ``[material]`` and ``[fluent]`` are the large sets, and large sets are large files — which matters when you freeze the application, since a font ships whole whether you use four glyphs or four thousand. See :doc:`../user-guide/packaging`.

**Drawing weight.** Sets are not interchangeable visually. Five packs, the same five things, each drawn the way that pack draws them when you pass no ``style``:

.. pack-comparison::

``[lucide]`` is light and even; ``[material]`` and ``[remix]`` default to a solid fill; ``[bootstrap]`` and ``[fontawesome]`` sit between them, and both offer the other cut as a style. Mixing two general-purpose sets in one interface usually looks like a mistake — mixing a UI set with a logo set does not.

**Styles.** Of the :packs-stat:`total`, :packs-stat:`styled` offer more than one style of the same icon, so you can use an outline normally and a fill for the selected state. The other :packs-stat:`unstyled` do not, and take no ``style`` argument. :doc:`../user-guide/icons-and-names` covers how a style is chosen.

**Vocabulary.** Names are upstream's own. If you already think in Font Awesome names, using that pack will feel faster than a set with better coverage but unfamiliar names.

Using two at once
-----------------

Common and supported — each icon holds its own icon set, so packs never interfere:

.. code-block:: bash

   pip install "tkinter-icons[lucide,simple]"

.. code-block:: python

   from tkinter_icons import LucideIcon, SimpleIcon

   save = LucideIcon("save", size=20)
   github = SimpleIcon("github", size=20)

The usual reason is a UI set plus a logo set: no general-purpose pack has a GitHub mark, and no logo pack has a "save" icon.

Still unsure?
-------------

Install two and look at them side by side:

.. code-block:: bash

   pip install "tkinter-icons[lucide,material]"
   tkinter-icons

The browser switches between installed sets from one dropdown, at whatever size and color you are actually going to use. That is a more useful comparison than any table, this one included.
