Meteocons
=========

Alessio Atzeni's weather set — ninety-four glyphs, hand-drawn, and much warmer in character than the systematic alternative. Where :doc:`weather` is a reference set with a symbol for every meteorological condition anyone has needed, Meteocons is a small, opinionated collection that looks drawn rather than specified.

Choose it when the weather is a feature of the interface rather than the subject of the application: a handful of conditions, drawn large, where the look matters more than the coverage. Choose :doc:`weather` when you need moon phases, wind direction, or a glyph for every code an API can return.

Alongside the weather symbols the font carries a full set of letters, numerals, and punctuation, drawn in the same hand.

.. pack-preview:: meteocons

Using it
--------

.. pack-install:: meteocons

.. code-block:: python

   from tkinter_icons import MeteoconsIcon

   sunny = MeteoconsIcon("sun", size=48)
   overcast = MeteoconsIcon("clouds", size=48)
   storm = MeteoconsIcon("thunderstorm", size=48)

At ninety-four glyphs it is the smallest pack in the catalogue by a long way, so it is also the cheapest to ship — see :doc:`../user-guide/packaging`.

Names
-----

Names are semantic, and the filled variants carry a ``-filled`` suffix rather than being a style:

.. code-block:: python

   MeteoconsIcon("cloud-sun")
   MeteoconsIcon("cloud-sun-filled")

.. note::

   Meteocons is free for personal and commercial use, with terms of its own that differ from the permissive licenses most packs here carry. See ``THIRD-PARTY-NOTICES.md`` in the repository before redistributing the font itself.

Pack details
------------

.. pack-facts:: meteocons
