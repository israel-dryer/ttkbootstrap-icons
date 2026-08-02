Stateful icons
==============

A ttk widget already changes color as you interact with it — its foreground is one color at rest, another on hover, another when disabled. An icon set as a plain image does not follow any of that, and a blue icon on a button whose text has gone grey looks broken.

:meth:`Icon.map <tkinter_icons.Icon.map>` fixes that in one call. The icon is re-rendered per state in the color the widget's own style uses for that state, and the results are mapped onto a child style applied to the widget.

.. image:: /assets/stateful_icons_demo.gif
   :alt: Buttons whose icons change color as the pointer moves over them

Following the theme automatically
---------------------------------

With no arguments beyond the widget, the icon reads the parent style's ``foreground`` map and renders itself once per state found there:

.. code-block:: python

   import tkinter as tk
   from tkinter import ttk

   from tkinter_icons import BootstrapIcon

   root = tk.Tk()

   icon = BootstrapIcon("house", size=16)
   button = ttk.Button(root, text="Home")
   button.pack(padx=20, pady=20)

   icon.map(button)

   root.mainloop()

.. image:: /assets/01_automatic_color_mapping.png
   :alt: An icon tinted to match each of the button's states

Note what is *not* in that code: no color. Passing one would pin the icon to it, which is the opposite of what this is for.

Choosing the colors yourself
----------------------------

Pass a ``statespec`` — a list of ``(state, spec)`` pairs, where the spec is a color:

.. code-block:: python

   icon.map(button, statespec=[
       ("pressed", "#0a58ca"),
       ("hover", "#0d6efd"),
       ("disabled", "#adb5bd"),
   ])

.. image:: /assets/02_custom_colors.png
   :alt: A button whose icon uses explicitly chosen per-state colors

States are matched first-match-wins, the way ttk state maps always work, so order them from most specific to least.

Changing the icon per state
---------------------------

The spec can be a dict instead, naming a different icon for that state — an outline that fills on hover, a play that becomes a pause:

.. code-block:: python

   icon.map(button, statespec=[
       ("hover", {"name": "house-fill"}),
       ("pressed", {"name": "house-fill", "color": "#0a58ca"}),
   ])

.. image:: /assets/03_icon_name_change.png
   :alt: A button whose icon swaps to its filled variant on hover

Give a dict without a ``color`` and the color still follows the parent style for that state; give both and both are yours.

Theme changes
-------------

Every mapped widget is tracked, and a ``<<ThemeChanged>>`` event re-renders all of them against their original parent style. Switching a ttkbootstrap theme at runtime therefore recolors the icons too, with nothing to call.

Tracking is per widget and released when the widget is destroyed, so mapped icons do not accumulate. :meth:`~tkinter_icons.Icon.unmap` exists for the rarer case of an icon that outlives its widget:

.. code-block:: python

   icon.unmap(button)

Merging, and the child style
----------------------------

``map()`` does not restyle the widget in place — it derives a **child style** from whatever style the widget already had, and applies that. The derived name is either ``"{subclass}.{ParentStyle}"`` when you pass ``subclass``, or a short hash of the icon names and size when you do not.

That distinction matters if you call ``map()`` more than once on the same widget. Two calls merge into one image map only when they land on the same child style name, and the generated name changes whenever the set of icon names does. Pass a stable ``subclass`` when you intend to build a mapping up in pieces:

.. code-block:: python

   icon.map(button, subclass="nav", statespec=[("hover", "#0d6efd")])
   icon.map(button, subclass="nav", statespec=[("disabled", "#adb5bd")])
   # one style, both states

``mode`` controls what happens to states already mapped on that child style:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Mode
     - Behaviour
   * - ``"merge"``
     - The default. Existing entries keep their order, incoming states overwrite matching ones, new states are appended.
   * - ``"replace"``
     - Ignore what is there and apply only the states given, plus the fallback.

A fallback for the empty state (``''``) is always included, rendered in the parent style's ordinary foreground, so a widget in a state you did not map still shows an icon.

Using it on your own widget class
---------------------------------

The mixin renders a state's image by constructing another instance of the icon's own class with ``(name, size, color)``. If your class takes something different, override :meth:`_render_icon` rather than working around the constructor:

.. code-block:: python

   class BadgedIcon(MaterialIcon):
       def _render_icon(self, name, size, color):
           return MaterialIcon(name, size, color or "black").image