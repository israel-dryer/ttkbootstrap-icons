Headless rendering
==================

The drawing core is pure Pillow. It has no Tkinter import anywhere in it, so anything that wants pixels rather than a widget image needs no display, no root window, and no event loop — a test suite on a CI runner with no ``$DISPLAY``, a build step that bakes PNGs, a server process generating thumbnails.

.. note::

   ``tkinter`` itself must still be importable, even though nothing here uses it: ``import tkinter_icons`` reaches the Tk-facing layer on the way to the renderer. On Linux that means the ``python3-tk`` package — see :doc:`../getting-started/installation`. Dropping that requirement is tracked in `issue #91 <https://github.com/israel-dryer/tkinter-icons/issues/91>`__.

.. versionadded:: 5.0.0
   :meth:`Icon.render_pil <tkinter_icons.Icon.render_pil>` and the pure-Pillow :func:`~tkinter_icons.render_glyph`, as the supported way in without a display.

Rendering to a Pillow image
---------------------------

:meth:`~tkinter_icons.Icon.render_pil` is a classmethod on the pack's icon class. It needs no root window:

.. code-block:: python

   from tkinter_icons import MaterialIcon

   image = MaterialIcon.render_pil("home", size=64, color="#0F766E")
   image.save("home.png")

The return is a square RGBA :class:`PIL.Image.Image`. A name the pack cannot resolve raises :class:`ValueError`, exactly as the constructor does — see :doc:`icons-and-names`, which also covers ``on_missing``, the policy for the different case where a name reaches an icon set that has no glyph for it.

.. versionchanged:: 5.1.0
   A name the pack could not resolve used to come back as a transparent image rather than raising. It is the headless path — build steps, export scripts, test suites — which is exactly where a blank PNG is least likely to be noticed and most likely to be committed.

Called on a pack's class it draws that pack's glyphs and takes the same friendly names the constructor takes, so nothing has to be set up first. Called on :class:`~tkinter_icons.Icon` itself there is no pack to draw from, and you have to say which set to use — see :ref:`explicit-icon-sets` below.

.. versionchanged:: 5.0.0
   ``render_pil`` used to read whichever icon set was initialized most recently, so it drew the right glyphs only if something had already constructed an icon from that pack — and raised in a fresh process. It also took an already-resolved glyph name, which meant a friendly name like ``"house-fill"`` rendered transparent.

Choosing a style
----------------

``render_pil`` takes ``style`` in the same position and with the same meaning as the constructor, and looks names up exactly the same way — see :ref:`how-a-name-finds-its-style`. Anything you can construct, you can render headlessly, and it resolves to the same glyph:

.. code-block:: python

   from tkinter_icons import FontAwesomeIcon

   FontAwesomeIcon("accusoft", size=32)                            # a brand mark
   FontAwesomeIcon.render_pil("accusoft", size=32)                 # the same glyph
   FontAwesomeIcon.render_pil("accusoft", size=32, style="brands") # said explicitly

Reach for ``style`` when a name exists in several styles and you want one that is not the pack's default:

.. code-block:: python

   FontAwesomeIcon.render_pil("address-book", size=32)                  # solid, the default
   FontAwesomeIcon.render_pil("address-book", size=32, style="regular") # the outlined cut

Unlike a bare name, an explicit ``style`` is never quietly dropped. Naming a style the pack does not draw that icon in, or one the name itself contradicts, raises rather than returning a blank image — the icon set is chosen from the style, so ignoring the argument would mean drawing the wrong style rather than drawing nothing:

.. code-block:: python

   FontAwesomeIcon.render_pil("accusoft", style="solid")
   # ValueError: accusoft not found in lookup for fontawesome in solid style.

It needs a provider to resolve against, so it belongs on a pack's class. Passing it to :class:`~tkinter_icons.Icon`, or alongside an explicit ``icon_set``, raises: that set already fixes the style, and there would be nothing left for the argument to do.

.. versionadded:: 5.1.0
   ``style`` on ``render_pil``. Before it, a name reachable through ``PackIcon(name, style=...)`` had no equivalent on the headless path.

If you already have an icon, :meth:`~tkinter_icons.Icon.to_pil` renders that exact icon:

.. code-block:: python

   icon = MaterialIcon("home", size=64, color="#0F766E")
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

.. _explicit-icon-sets:

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
       color="#0F766E",
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