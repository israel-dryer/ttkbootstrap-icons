Devicon
=======

Logos for programming languages, frameworks, databases, and developer tooling — the set you want for a project list, a language picker, or a status bar that names the stack it is watching.

It is narrower than :doc:`simple` and organized differently. Devicon gives most marks in more than one form: a ``plain`` outline, the logo's own shape as ``original``, and ``-wordmark`` variants of each that include the lettering. Not every mark has all four, so the ``original`` cuts are a good deal smaller than the ``plain`` one.

Like :doc:`simple`, this is not a UI set — pair it with a general-purpose pack.

.. pack-preview:: devicon

Using it
--------

.. pack-install:: devicon

.. code-block:: python

   from tkinter_icons import DeviconIcon

   docker = DeviconIcon("docker", size=24)                        # plain, the default
   react = DeviconIcon("react", size=24, style="original")
   python = DeviconIcon("python", size=24, style="plain-wordmark")

.. important::

   ``original`` names the logo's *shape*, not its colors. Every glyph in this pack is a single-color drawing, because that is what a font glyph is — you choose the color with ``color=``, and a multicolored mark comes out as one silhouette. For a brand's official color, pass it yourself:

   .. code-block:: python

      DeviconIcon("python", size=24, color="#3776AB")

Names
-----

The style is part of the upstream name, and both spellings work:

.. code-block:: python

   DeviconIcon("react-original-wordmark")
   DeviconIcon("react", style="original-wordmark")   # the same glyph

Coverage varies by style. ``python`` has a ``plain`` cut but no ``original`` one; asking for a style a mark does not have raises rather than falling back.

Pack details
------------

.. pack-facts:: devicon
