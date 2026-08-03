Remix Icon
==========

A neutral system set drawn on a strict 24px grid, with a line and a fill cut of essentially everything. Remix is deliberately characterless in the way a system font is characterless — it does not impose a look, which is what you want when the application has one of its own.

Against :doc:`bootstrap` it is more evenly weighted and rather more complete; against :doc:`lucide` it is heavier and gives you a filled state to switch to. It is the safe pick when none of the sets with more personality fits.

.. pack-preview:: remix

Using it
--------

.. pack-install:: remix

.. code-block:: python

   from tkinter_icons import RemixIcon

   home = RemixIcon("home", size=20, style="line")
   home_selected = RemixIcon("home", size=20)          # fill, the default
   delete = RemixIcon("delete-bin", size=20, style="line")

Names
-----

Upstream names carry the cut as a ``-line`` or ``-fill`` suffix, and both spellings work:

.. code-block:: python

   RemixIcon("settings-line")
   RemixIcon("settings", style="line")   # the same glyph

Remix numbers its variants rather than describing them — ``home-2``, ``home-3``, and so on up to ``home-8`` are all different houses. The browser is the fast way to see which one you want; see :doc:`../user-guide/icon-browser`.

Pack details
------------

.. pack-facts:: remix
