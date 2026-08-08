Bootstrap Icons
===============

Bootstrap's own set, drawn by the framework's maintainers and shaped by the same conventions: moderate stroke weight, rounded corners, and an outline and a fill for most of the vocabulary. If you have built anything for the web in the last decade, the names are already in your head.

Reach for it when you are on plain ``tkinter``/``ttk`` and want the Bootstrap look, or when you want a matched outline/fill pair without stepping up to one of the very large sets. If you are already using `ttkbootstrap <https://github.com/israel-dryer/ttkbootstrap>`__, note that it builds these glyphs in — see :doc:`../integrations/ttkbootstrap` before installing this pack alongside it.

.. pack-preview:: bootstrap

Using it
--------

.. pack-install:: bootstrap

The outline/fill pair is what this set is for. Draw the outline normally and swap the fill in for the selected item, and the two line up because they are the same drawing:

.. code-block:: python

   from tkinter_icons import BootstrapIcon

   star = BootstrapIcon("star", size=20)
   starred = BootstrapIcon("star", size=20, style="fill")

   button.configure(image=starred.image if favorite else star.image)

Names
-----

Fill is spelled either way — as a ``style`` argument or as a ``-fill`` suffix, which is how the upstream site lists it:

.. code-block:: python

   BootstrapIcon("gear-fill")
   BootstrapIcon("gear", style="fill")   # the same glyph

Omitting ``style`` gives you the outline. A ``-fill`` name with ``style="outline"`` is an error rather than a silent preference — see :doc:`../user-guide/icons-and-names`.

Pack details
------------

.. pack-facts:: bootstrap
