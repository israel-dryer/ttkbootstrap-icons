Eva Icons
=========

A small, rounded UI set from Akveo, with an outline and a fill for very nearly every icon — the two cuts are within a few glyphs of the same size, which is unusual and makes the pairing dependable.

It is one of the smaller general-purpose sets here, and that is the thing to weigh. Eva covers the common interface vocabulary and stops; if your application needs anything specific, check the count against :doc:`material` or :doc:`remix` before committing. What you get in exchange is a soft, friendly drawing style that the more systematic sets do not have.

.. pack-preview:: eva

Using it
--------

.. pack-install:: eva

.. code-block:: python

   from tkinter_icons import EvaIcon

   home = EvaIcon("home", size=20, style="outline")
   home_selected = EvaIcon("home", size=20)        # fill, the default
   settings = EvaIcon("settings-2", size=20, style="outline")

Names
-----

Outline names carry an ``-outline`` suffix upstream, and both spellings work:

.. code-block:: python

   EvaIcon("person-outline")
   EvaIcon("person", style="outline")   # the same glyph

Pack details
------------

.. pack-facts:: eva
