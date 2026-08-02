Font Awesome 6 (Free)
=====================

The set most people mean when they say "icon font". Font Awesome's free tier is what this pack carries, and its three styles cover two different jobs at once: ``solid`` and ``regular`` are the interface glyphs, and ``brands`` is several hundred company and product marks.

That pairing is the reason to pick it. Most general-purpose sets have no logos at all, so using one of those usually means installing a second pack — :doc:`simple` or :doc:`devicon` — for the brand marks. Here they come in the same font.

The trade-off is that ``regular`` is much smaller than ``solid``: the free tier keeps most of the outline cut behind Font Awesome Pro, so an icon that exists as a solid often has no regular counterpart.

.. pack-preview:: fontawesome

Using it
--------

.. pack-install:: fontawesome

.. code-block:: python

   from tkinter_icons import FontAwesomeIcon

   home = FontAwesomeIcon("house", size=20)                    # solid, the default
   saved = FontAwesomeIcon("floppy-disk", size=20, style="regular")
   github = FontAwesomeIcon("github", size=20, style="brands")

``brands`` is a separate vocabulary rather than a second cut of the same one — ``github`` exists only there, and ``house`` does not exist there at all.

Pack details
------------

.. pack-facts:: fontawesome
