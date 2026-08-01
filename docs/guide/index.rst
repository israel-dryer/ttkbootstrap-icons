User guide
==========

How the library works, independent of which GUI framework you have wrapped around Tk. Framework-specific idioms live in :doc:`../integrations/index`.

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

.. toctree::
   :hidden:

   icons-and-names
   sizing-and-quality
   stateful-icons
   headless-rendering
   icon-browser
   packaging
