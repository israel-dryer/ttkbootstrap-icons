:html_theme.sidebar_secondary.remove: true

tkinter-icons
=============

Font-based icons for Tkinter — sixteen icon sets, one import root, no image files to manage.

.. code-block:: python

   from tkinter_icons import MaterialIcon

   icon = MaterialIcon("home", size=24, color="#0d6efd")
   ttk.Button(root, text="Home", image=icon.image, compound="left").pack()

An icon is a glyph from an icon font, rendered to a Tk image at the size and color you ask for. Nothing is loaded from disk at import time, nothing is drawn until you use it, and identical icons share one image.

.. container:: hero-ctas

   .. button-ref:: getting-started
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

Install a pack, not a library
-----------------------------

The base install is a renderer with no glyphs of its own. The icons come from packs, and you install one as an extra:

.. code-block:: bash

   pip install "tkinter-icons[material]"

That is the whole model: **one library, sixteen installable icon packs**. They are separate distributions because each ships its own font — bundling all of them would cost about 17 MB to give most people fifteen icon sets they will never open — but you never install them by name. :doc:`packs` compares the sixteen.

.. important::

   Every install line in these docs carries an extra. A bare ``pip install tkinter-icons`` gets you a renderer that draws nothing, and asking for an icon class then raises with the command you actually wanted.

Why you might want this
-----------------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Sixteen sets, one API

      Material, Font Awesome, Lucide, Bootstrap, Simple Icons, weather symbols, developer logos, fantasy glyphs. Every pack's class takes the same ``(name, size, color, style)``, so switching sets is a one-line change.

   .. grid-item-card:: Sharp at any size

      Glyphs are centered on their measured ink rather than on the font's own bounding box, which under-reports it. Odd sizes snap even, small sizes render oversampled and downscale with a light sharpen.

   .. grid-item-card:: Renders without a display

      :meth:`Icon.render_pil <tkinter_icons.Icon.render_pil>` returns a Pillow image and touches no Tk, so icons work in a test suite, a build step, or a server process.

   .. grid-item-card:: Follows your ttk theme

      Map an icon onto a widget and its tint follows that widget's per-state foreground — hover, pressed, disabled — and re-renders itself when the theme changes.

Is this the right library?
--------------------------

**Use it if** you are writing plain ``tkinter``/``ttk``, or you want an icon set other than Bootstrap.

**You may not need it if** you are using `ttkbootstrap <https://github.com/israel-dryer/ttkbootstrap>`_ or `bootstack <https://github.com/israel-dryer/bootstack>`_ *and* Bootstrap Icons are all you want — both have those built in. This library is still useful alongside either one when you want a different set; see :doc:`integrations/ttkbootstrap`.

.. note::

   This project was published as ``ttkbootstrap-icons`` through 4.0.0. It was renamed in 5.0.0 because the old name described a relationship that no longer exists. Your existing code keeps working — see :ref:`migrating`.

.. toctree::
   :hidden:
   :caption: Getting started

   getting-started
   packs

.. toctree::
   :hidden:
   :caption: User guide

   guide/icons-and-names
   guide/sizing-and-quality
   guide/stateful-icons
   guide/headless-rendering
   guide/icon-browser
   guide/packaging

.. toctree::
   :hidden:
   :caption: Integrations

   integrations/tkinter-ttk
   integrations/ttkbootstrap

.. toctree::
   :hidden:
   :caption: Reference

   api
   contributing

.. toctree::
   :hidden:
   :caption: About

   release-notes
   license