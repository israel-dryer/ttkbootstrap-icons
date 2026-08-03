User guide
==========

Everything from installing a pack to freezing an application. The library itself is framework-neutral, so the guides below describe it independently of whatever you have wrapped around Tk; framework-specific idioms live under Integrations, at the end.

Getting started
---------------

Four short pages: install a pack, draw an icon, work out which set you want, and — if you are arriving from ``ttkbootstrap-icons`` — move your existing code over.

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Installation
      :link: ../getting-started/installation
      :link-type: doc

      Installing a pack as an extra, what the quotes are for, and what the base package does not give you.

   .. grid-item-card:: Quickstart
      :link: ../getting-started/quickstart
      :link-type: doc

      An icon on a button in ten lines, and the three things about it that matter later.

   .. grid-item-card:: Choosing a pack
      :link: ../getting-started/choosing-a-pack
      :link-type: doc

      Sixteen sets, and how to pick without reading all of them.

   .. grid-item-card:: Migrating
      :link: ../getting-started/migrating
      :link-type: doc

      Coming from ``ttkbootstrap-icons`` 4.0.0. Your code keeps working; the imports and the centering are what change.

Feature guides
--------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Icons and names
      :link: icons-and-names
      :link-type: doc

      How a name resolves, what styles are, and what happens when a name is wrong.

   .. grid-item-card:: Sizing and render quality
      :link: sizing-and-quality
      :link-type: doc

      Sizes, padding, sharpness, and every knob on ``RenderOptions``.

   .. grid-item-card:: Stateful icons
      :link: stateful-icons
      :link-type: doc

      Icons that follow a widget's hover, pressed, and disabled colors.

   .. grid-item-card:: Headless rendering
      :link: headless-rendering
      :link-type: doc

      Pillow images with no Tk and no display — tests, build steps, servers.

   .. grid-item-card:: Icon browser
      :link: icon-browser
      :link-type: doc

      Find the name you need without guessing.

   .. grid-item-card:: Packaging
      :link: packaging
      :link-type: doc

      Shipping an application whose icons still work once frozen.

Integrations
------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: tkinter and ttk
      :link: ../integrations/tkinter-ttk
      :link-type: doc

      Buttons, menus, trees, notebooks, canvases, and the window icon — plus the reference-keeping rule that catches everyone once.

   .. grid-item-card:: ttkbootstrap
      :link: ../integrations/ttkbootstrap
      :link-type: doc

      Using another icon set inside ttkbootstrap, and letting the theme choose the color.

.. Three captioned toctrees rather than one flat list: the sidebar groups match
   the three headings above, so the page and the sidebar agree. The pages
   themselves stay in `getting-started/` — nav structure is a toctree question
   in Sphinx, not a directory one, and moving the files would break every
   cross-reference and every URL to buy nothing.

.. toctree::
   :hidden:
   :caption: Getting started

   ../getting-started/installation
   ../getting-started/quickstart
   ../getting-started/choosing-a-pack
   ../getting-started/migrating

.. toctree::
   :hidden:
   :caption: Feature guides

   icons-and-names
   sizing-and-quality
   stateful-icons
   headless-rendering
   icon-browser
   packaging

.. toctree::
   :hidden:
   :caption: Integrations

   ../integrations/tkinter-ttk
   ../integrations/ttkbootstrap
