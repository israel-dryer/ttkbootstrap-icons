Headless rendering
==================

The drawing core is pure Pillow. It has no Tkinter import anywhere in it, so anything that wants pixels rather than a widget image can skip Tk entirely — a test suite on a CI runner with no display, a build step that bakes PNGs, a server process generating thumbnails.

.. versionadded:: 5.0.0
   :meth:`Icon.render_pil <tkinter_icons.Icon.render_pil>` and the pure-Pillow :func:`~tkinter_icons.render_glyph`, as the supported way in without a display.

Rendering to a Pillow image
---------------------------

:meth:`~tkinter_icons.Icon.render_pil` is a classmethod on the pack's icon class. It needs no root window:

.. code-block:: python

   from tkinter_icons import MaterialIcon

   image = MaterialIcon.render_pil("home", size=64, color="#0d6efd")
   image.save("home.png")

The return is a square RGBA :class:`PIL.Image.Image`. A name that is not in the set comes back fully transparent rather than raising, subject to the ``on_missing`` policy described in :doc:`icons-and-names`.

.. warning::

   ``render_pil`` renders from the *active* icon set, which is whichever pack was initialized most recently. Constructing any icon from a pack initializes it, which is why the example above imports ``MaterialIcon`` and calls the classmethod on it. To be explicit — or to render from two packs in one process — pass ``icon_set`` (below).

If you already have an icon, :meth:`~tkinter_icons.Icon.to_pil` renders that exact icon:

.. code-block:: python

   icon = MaterialIcon("home", size=64, color="#0d6efd")
   icon.to_pil().save("home.png")

Exporting a set of icons
------------------------

.. code-block:: python

   from pathlib import Path

   from tkinter_icons import MaterialIcon

   out = Path("icons")
   out.mkdir(exist_ok=True)

   for name in ("home", "cog", "account-circle", "magnify"):
       for size in (16, 24, 32):
           image = MaterialIcon.render_pil(name, size=size, color="#212529")
           image.save(out / f"{name}-{size}.png")

No root window is created anywhere in that loop, so it runs under ``xvfb``-less CI, in a container, or from a build script.

Being explicit about the icon set
---------------------------------

An :class:`~tkinter_icons.IconSet` is one pack's glyphs in one style — the font bytes, the name-to-character map, the ink metrics, and the pack's default options — as one immutable value. Pass one and nothing depends on which pack happened to be touched last:

.. code-block:: python

   from tkinter_icons import Icon, get_icon_set
   from tkinter_icons_bs import BootstrapFontProvider

   outline = get_icon_set(BootstrapFontProvider(), "outline")
   fill = get_icon_set(BootstrapFontProvider(), "fill")

   Icon.render_pil("house", size=32, icon_set=outline)
   Icon.render_pil("house-fill", size=32, icon_set=fill)

Icon sets are cached by identity, so building the same one twice is free and two packs can be live at once without interfering.

Drawing a glyph directly
------------------------

Below :class:`~tkinter_icons.Icon` there is :func:`~tkinter_icons.render_glyph`, which knows nothing about packs or names — you hand it a character and a font:

.. code-block:: python

   from tkinter_icons import RenderOptions, render_glyph

   icon_set = MaterialIcon("home").icon_set

   image = render_glyph(
       icon_set.glyph("home"),
       size=64,
       color="#0d6efd",
       font_key=icon_set.font_key,
       font_bytes=icon_set.font_bytes,
       ink=icon_set.ink("home"),
       options=RenderOptions(pad_factor=0.0),
   )

This is the layer the rest is built on, and it is public so that an asset pipeline can use it without pretending to be a GUI. Omit ``ink`` and the glyph is measured at draw time instead — less accurate, and the reason the packs ship metrics at all. See :doc:`sizing-and-quality`.

Testing icons
-------------

Because rendering is pure Pillow, an icon is testable by looking at its pixels:

.. code-block:: python

   def test_icon_is_not_blank():
       image = MaterialIcon.render_pil("home", size=32, color="black")
       assert image.size == (32, 32)
       assert image.getchannel("A").getbbox() is not None    # something was drawn

   def ink_width(image):
       left, _, right, _ = image.getchannel("A").getbbox()
       return right - left

   def test_padding_shrinks_the_glyph():
       tight = MaterialIcon.render_pil("home", 64, options=RenderOptions(pad_factor=0.0))
       padded = MaterialIcon.render_pil("home", 64, options=RenderOptions(pad_factor=0.25))
       assert ink_width(tight) > ink_width(padded)

.. note::

   The caches behind fonts and icon sets are plain dictionaries, and no locking is implemented. Rendering is safe to call from a single thread — including a thread that is not the Tk thread, since nothing here touches Tk — but a worker pool sharing these caches is not something the library currently guarantees.