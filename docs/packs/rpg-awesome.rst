RPG Awesome
===========

Swords, shields, potions, monsters, spell effects, and armour. This is a set for games, character sheets, and inventory screens, and it is the only pack in the catalog that has nothing to do with interface chrome.

There is no reason to compare it with the others — nothing else here draws a dragon, and it does not draw a "save" icon. Install it alongside a general-purpose pack and use each for what it is for.

.. pack-preview:: rpg-awesome

Using it
--------

.. pack-install:: rpg-awesome

.. code-block:: python

   from tkinter_icons import RpgAwesomeIcon

   weapon = RpgAwesomeIcon("broadsword", size=32)
   armour = RpgAwesomeIcon("shield", size=32)
   potion = RpgAwesomeIcon("potion", size=32)

The drawings carry a lot of internal detail, so this set wants to be rendered larger than a UI set would — 24px and up. Below that it turns to mush; :doc:`../user-guide/sizing-and-quality` explains what the renderer can and cannot do about that.

Names
-----

Upstream names are prefixed ``ra-``, and both spellings resolve:

.. code-block:: python

   RpgAwesomeIcon("ra-crossed-swords")
   RpgAwesomeIcon("crossed-swords")   # the same glyph

Pack details
------------

.. pack-facts:: rpg-awesome
