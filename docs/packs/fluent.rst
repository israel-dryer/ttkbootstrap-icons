Fluent System Icons
===================

Microsoft's system set, and the second largest here. It is drawn for Windows, so on Windows it is the set most likely to look like the rest of the desktop.

Its distinguishing feature is that the design size is part of the icon, not just the render size. Fluent draws separate glyphs for 16, 20, 24, 28, 32 and up — the 16px drawing is not the 24px one shrunk, it has fewer details and a heavier line so that it survives at 16px. You pick the drawing that matches the size you are rendering at.

The ``light`` style is a small subset, not a third full cut: it exists only at 32px and covers a few hundred common icons. If you want only the regular weight and not the file size that comes with all three, :doc:`fluent-regular` is the same drawings in a much smaller font.

.. pack-preview:: fluent

Using it
--------

.. pack-install:: fluent

.. code-block:: python

   from tkinter_icons import FluentIcon

   home = FluentIcon("home-24", size=24)
   home_small = FluentIcon("home-20", size=20)
   home_selected = FluentIcon("home-24", size=24, style="filled")

Names
-----

Upstream spells every name ``ic-fluent-<icon>-<size>-<style>``, which is what you will see on GitHub and what the browser lists. You do not have to type it: the prefix is optional, and so is the style suffix when you pass ``style`` instead. All four of these resolve to the same glyph.

.. code-block:: python

   FluentIcon("ic-fluent-save-24-regular")
   FluentIcon("save-24-regular")
   FluentIcon("save-24", style="regular")
   FluentIcon("save-24")                    # regular is the default

The one segment that is not filler is ``-<size>-``, and it should match the ``size`` you pass. Nothing enforces it — a 24px drawing rendered at 16px is legal and merely looks muddy, which is exactly what the separate drawings exist to avoid.

Giving both a style suffix and a ``style`` argument is fine as long as they agree; a disagreement is an error rather than a silent preference.

Pack details
------------

.. pack-facts:: fluent
