Typicons
========

A small, sturdy set from an earlier era of icon design — heavier and more literal than anything else in the catalogue, drawn to read at 16px on screens that were not sharp. Stephen Hutchings has maintained it for over a decade.

It is the smallest general-purpose set here, so pick it for the drawing rather than the coverage. Where :doc:`lucide` is a thin even line and :doc:`remix` is a neutral grid, Typicons is solid and slightly chunky, and it holds together at sizes where lighter sets start to disappear.

Note that the fill cut is more than twice the size of the outline cut: a lot of these icons exist only filled.

.. pack-preview:: typicons

Using it
--------

.. pack-install:: typicons

.. code-block:: python

   from tkinter_icons import TypiconsIcon

   home = TypiconsIcon("home", size=20)                        # fill, the default
   home_outline = TypiconsIcon("home", size=20, style="outline")
   settings = TypiconsIcon("cog", size=20)

As with :doc:`material`, the gear is ``cog``. The ``-outline`` suffix and ``style="outline"`` are equivalent.

Pack details
------------

.. pack-facts:: typicons
