Lucide Icons
============

The most consistent set here. Lucide is a community-maintained continuation of Feather, and it keeps Feather's discipline: one stroke weight, one corner radius, one grid, applied to every glyph. Nothing in it is heavier or lighter than anything else in it.

That evenness is the reason to choose it, and it is also the trade-off. There is no fill, so you cannot express a selected state by weight — you express it with colour, or with a background. Against :doc:`material`, Lucide is a fraction of the size and a much lighter line; against :doc:`bootstrap`, it is quieter and has no filled counterpart.

.. pack-preview:: lucide

Using it
--------

.. pack-install:: lucide

No styles, so the constructor is just name, size, and colour:

.. code-block:: python

   from tkinter_icons import LucideIcon

   save = LucideIcon("save", size=20)
   folder = LucideIcon("folder-open", size=20)
   search = LucideIcon("search", size=20, color="#0F766E")

Because the stroke weight is fixed, Lucide holds up better than most sets at small sizes — but it is still a stroke, so see :doc:`../user-guide/sizing-and-quality` before drawing below about 16px.

Pack details
------------

.. pack-facts:: lucide
