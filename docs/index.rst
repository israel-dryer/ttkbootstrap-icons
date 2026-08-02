:html_theme.sidebar_secondary.remove: true

tkinter-icons
=============

Font-based icons for Tkinter — :packs-stat:`icons` icons across :packs-stat:`total` sets, one import, no image files to manage.

.. icon-hero::

.. container:: hero-ctas

   .. button-ref:: getting-started/installation
      :ref-type: doc
      :color: primary
      :class: sd-px-4 sd-fs-5

      Get started

   .. button-ref:: packs
      :ref-type: doc
      :color: secondary
      :outline:
      :class: sd-px-4 sd-fs-5

      Browse the packs

.. container:: hero-meta

   MIT licensed · Python 3.10+ · Pillow is the only dependency

Copy this and run it:

.. code-block:: python

   import tkinter as tk
   from tkinter import ttk

   from tkinter_icons import MaterialIcon

   root = tk.Tk()

   home = MaterialIcon("home", size=24, color="#0F766E")
   ttk.Button(root, text="Home", image=home.image, compound="left").pack(padx=20, pady=20)

   root.mainloop()

An icon is a glyph from an icon font, rendered to a Tk image at the size and color you ask for. Nothing is loaded from disk at import time, nothing is drawn until you use it, and identical icons share one image.

Install a pack, not a library
-----------------------------

One line puts a full icon set in your project:

.. code-block:: bash

   pip install "tkinter-icons[material]"

That is the whole model: **one library, sixteen installable icon packs**. Name the extra, import from ``tkinter_icons``, and the distribution names never come up — the base package is the renderer, and the glyphs come from the pack you named. :doc:`packs` compares the sixteen.

What you get
------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Sixteen sets, one API

      Material, Font Awesome, Lucide, Bootstrap, Simple Icons, weather symbols, developer logos, fantasy glyphs. Every pack's class takes the same ``(name, size, color, style)``, so switching sets is a one-line change.

   .. grid-item-card:: Sharp at any size

      Glyphs are centered on their measured ink rather than on the font's own bounding box, which under-reports it. Odd sizes snap even, small sizes render oversampled and downscale with a light sharpen.

   .. grid-item-card:: No image assets to manage

      Size and color are arguments, not files. No ``icons/`` directory, no ``@2x`` duplicates, no second set for dark mode — ask for 16px grey and 32px teal from the same glyph.

   .. grid-item-card:: Follows your ttk theme

      Map an icon onto a widget and its tint follows that widget's per-state foreground — hover, pressed, disabled — and re-renders itself when the theme changes.

Coming from ttkbootstrap-icons? Your existing code keeps working — :doc:`getting-started/migrating` is a five-minute read.

.. container:: hero-ctas

   .. button-ref:: getting-started/installation
      :ref-type: doc
      :color: primary
      :class: sd-px-4 sd-fs-5

      Install a pack and draw your first icon

.. Every entry here becomes a top-level item in the header nav. Anything past
   the fifth is folded into a "More" dropdown, and enough of them overflow the
   bar entirely — which is what listing all fifteen pages, and then all eight
   sections, each did in turn. Depth belongs in the sidebar, not across the top.

   Getting started is a captioned group *inside* the user guide rather than a
   top-level entry of its own: the boundary between "quickstart" and "icons and
   names" was never clear enough to justify a nav split, and folding it in puts
   the reading order — install, draw, choose, then the guides — in one sidebar.

.. toctree::
   :hidden:
   :maxdepth: 2

   user-guide/index
   packs
   api
   about/index