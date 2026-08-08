Material Design Icons
=====================

The largest set in the catalog, and by a wide margin. This is the Pictogrammers library — Google's Material set as a starting point, then extended by the community for years past it, which is why it has a glyph for things no other set here covers.

Pick it when coverage is the deciding factor. The cost is size: the font is the biggest of the sixteen, which matters when you freeze an application, since a font ships whole whether you use four glyphs or four thousand. See :doc:`../user-guide/packaging`.

It is not the same pack as :doc:`google-material`, which is Google's own set and stops where Google stopped.

.. pack-preview:: material

Using it
--------

.. pack-install:: material

.. code-block:: python

   from tkinter_icons import MaterialIcon

   save = MaterialIcon("content-save", size=20)
   folder = MaterialIcon("folder-open", size=20)
   search = MaterialIcon("magnify", size=20)

Names
-----

Material's vocabulary is its own, and it is the most likely of any pack here to disagree with the word you would have guessed — the gear is ``cog``, search is ``magnify``, and save is ``content-save``. Run ``tkinter-icons`` and search rather than guessing; see :doc:`../user-guide/icon-browser`.

Fill is the default here, which is the opposite of :doc:`bootstrap`. Most of the set is filled; the outline cut is smaller and its names carry an ``-outline`` suffix upstream:

.. code-block:: python

   MaterialIcon("account")                      # filled
   MaterialIcon("account", style="outline")
   MaterialIcon("account-outline")              # the same glyph

Pack details
------------

.. pack-facts:: material
