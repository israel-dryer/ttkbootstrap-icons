Google Material Icons
=====================

Google's own icon set, in four cuts of every glyph. Unlike most packs with styles, the cuts here are not a weight pairing — every icon exists in all four, so ``baseline``, ``outlined``, ``round``, and ``sharp`` are a choice you make once for the whole application rather than per icon.

Choose it over :doc:`material` when you want Google's set as Google draws it. :doc:`material` starts from the same place and has been extended by the community well past it, so it covers far more but drifts from the Material specification in the process.

.. pack-preview:: google-material

Using it
--------

.. pack-install:: google-material

Set the style once and the whole interface stays in one cut:

.. code-block:: python

   from tkinter_icons import GoogleMaterialIcon
   from functools import partial

   Icon = partial(GoogleMaterialIcon, size=20, style="outlined")

   home = Icon("home")
   settings = Icon("settings")
   folder = Icon("folder")

Names
-----

Google's names use underscores rather than hyphens, which is the one thing that catches people coming from any other pack here:

.. code-block:: python

   GoogleMaterialIcon("settings_suggest")
   GoogleMaterialIcon("add_home_work")

Pack details
------------

.. pack-facts:: google-material
