Sizing and render quality
=========================

Most of the time ``size=`` and ``color=`` are all you need. This page is about what happens underneath, and the knobs for when the defaults are wrong for your case.

Size
----

``size`` is the edge of the square image, in pixels:

.. code-block:: python

   MaterialIcon("home", size=16)    # beside 10-11pt text
   MaterialIcon("home", size=24)    # toolbar button
   MaterialIcon("home", size=48)    # empty-state illustration

**Odd sizes snap up to even.** ``size=15`` renders 16 pixels. At fractional display scaling — 125%, 150%, the common Windows settings — an odd pixel size lands the glyph on a half-pixel boundary and LANCZOS smears it. Rounding up removes that at a cost of one pixel.

The icon reports both numbers, and layout code should use the second:

.. code-block:: python

   icon = MaterialIcon("home", size=15)
   icon.size             # 15
   icon.rendered_size    # 16

Turn it off with ``snap_even=False`` if you need the exact number more than you need the sharpness.

Color
-----

Anything Pillow accepts: a name, a hex string, an ``rgb()`` string.

.. code-block:: python

   MaterialIcon("home", color="black")
   MaterialIcon("home", color="#0F766E")
   MaterialIcon("home", color="rgb(15, 118, 110)")

Color is part of the cache key, so the same icon in three colors is three images. For an icon that should follow a widget's own colors as the user interacts with it, don't set the color at all — see :doc:`stateful-icons`.

How a glyph gets centered
-------------------------

This is the part 5.0.0 rebuilt, and it is worth one paragraph because it explains a visible change.

An icon font's glyphs do not fill their em box, and they do not fill it consistently. Pillow's ``font.getbbox()`` under-states the actual ink, so a glyph fitted to it lands well inside the box it was given — the faint inner square is what ``pad_factor`` reserves, and what the ink is supposed to fill:

.. renderer-figure:: measured-ink

It also places the glyph against the font's ascent and descent rather than against the glyph's own ink, so where the two disagree the icon rides high in its frame — far enough, in a set like Weather, to clip:

.. renderer-figure:: measured-ink-centering

Both are the same glyph at the same requested size, and neither panel is exaggerated. Across every glyph in every style of all sixteen packs, each drawn with its own pack's options, the ``getbbox`` path fills a per-pack median of 73% to 96% of the padded box, sits up to a median 10 pixels off-center at this size, and pushes **518 of the 89,169 glyphs that draw any ink** past the edge of the frame. Measured ink fills 94% to 102%, centers within half a pixel everywhere, and overflows **none** of the 89,169.

So the real ink is measured instead, once, offline: every glyph in every pack is rendered at 512 pixels, its true inked bounds are measured, and the result is stored as fractions of the em in that pack's ``metrics.json``. Fractions scale, so one measurement serves every render size. The renderer fits and centers on *that*.

A pack with no metrics still renders — the ``getbbox`` path is the fallback — but it renders the way 4.x did. All sixteen packs ship metrics as of their 1.1.0 release, so the right-hand panels above are not a state you can install your way into; they are what the renderer falls back to for a pack that ships none.

.. versionchanged:: 5.0.0
   Glyphs are centered on measured ink rather than on ``font.getbbox()``. Full-bleed icons gain their padding and the rest sit a little more centered. If you compensated for the old behaviour with your own padding, remove it.

RenderOptions
-------------

Every drawing knob lives on one immutable value. A pack supplies its own defaults — Font Awesome uses more padding than Bootstrap, for example — and you override per icon:

.. code-block:: python

   from tkinter_icons import MaterialIcon, RenderOptions

   tight = RenderOptions(pad_factor=0.0)
   MaterialIcon("home", size=32, options=tight)

Start from the pack's defaults rather than from scratch, so you change one thing and inherit the rest:

.. code-block:: python

   icon = MaterialIcon("home", size=32)
   sharper = icon.options.merge(align=True, oversample=4)
   MaterialIcon("home", size=32, options=sharper)

:meth:`~tkinter_icons.RenderOptions.merge` ignores ``None``, so optional arguments can be passed straight through without checking them first.

.. list-table::
   :header-rows: 1
   :widths: 18 12 70

   * - Option
     - Default
     - What it does
   * - ``pad_factor``
     - ``0.10``
     - Fraction of the frame kept as padding on each edge. ``0.0`` fills the frame; raise it for an icon that reads as too heavy next to text.
   * - ``scale_to_fit``
     - ``True``
     - Shrink the glyph so its ink fits the padded box. With ``False`` the glyph is drawn at frame size and only centered, so oversized glyphs clip.
   * - ``oversample``
     - auto
     - Render at this multiple of the target size, then downscale. ``None`` picks by size: 3× below 32 px, 2× below 64 px, 1× above.
   * - ``sharpen``
     - ``True``
     - Light unsharp mask after downscaling, restoring the edge contrast LANCZOS softens. No effect when not oversampling.
   * - ``align``
     - ``False``
     - Snap the draw origin to the final image's pixel grid. Crisper for a standalone mark that fills its frame; off by default so glyphs beside text keep exact optical centering.
   * - ``snap_even``
     - ``True``
     - Round the requested size up to an even number of pixels.
   * - ``y_bias``
     - ``0.0``
     - Extra vertical offset as a fraction of the frame, applied after centering. Rarely needed now that centering works from measured ink.

Two of those are easier seen than described. **Padding** is a fraction of the frame taken off every edge, and the glyph's ink is fitted to what remains — the faint inner square:

.. renderer-figure:: padding

**Oversampling** draws at a multiple of the target size and downscales, which is what keeps a small icon from losing its thin strokes. A 16-pixel Bootstrap gear, magnified six times with no smoothing so the pixels are the renderer's own:

.. renderer-figure:: oversampling

Two combinations worth knowing:

**A crisp standalone mark** — a window icon, a large empty-state glyph:

.. code-block:: python

   crisp = RenderOptions(pad_factor=0.0, align=True)

**An icon that sits beside text** — leave ``align`` off. Snapping to the pixel grid moves the glyph by up to half a pixel, which is invisible on its own and visible when it is next to a baseline.

Caching and memory
------------------

Rendered images are cached per Tk interpreter, keyed on the icon set, name, size, color, and options. The cache is dropped when its root window is destroyed, because a ``PhotoImage`` belongs to the interpreter that created it — a global cache would hand out dead handles the moment an application replaced its root, which is exactly what test suites do.

You rarely need to manage this, but the controls exist:

.. code-block:: python

   from tkinter_icons import Icon

   Icon.cache_info()     # {'interpreters': 1, 'images': 12, 'transparent': 1, 'icon_sets': 1}
   Icon.clear_cache()    # drop rendered images, keep fonts and glyph data
   Icon.cleanup()        # drop everything, including loaded fonts

:meth:`~tkinter_icons.Icon.clear_cache` is the one to call after something changes how icons should look. :meth:`~tkinter_icons.Icon.cleanup` is for a long-running process that is finished with icons entirely; nothing is written to disk, so it is about memory rather than correctness.