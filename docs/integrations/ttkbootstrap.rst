ttkbootstrap
============

`ttkbootstrap <https://github.com/israel-dryer/ttkbootstrap>`_ is a themed widget library for tkinter. It has Bootstrap icons built in, so if Bootstrap icons are all you need, you do not need this library at all.

You do need it when you want **a different icon set** — Material, Lucide, Font Awesome, brand marks — inside a ttkbootstrap application. Everything works, because a ttkbootstrap ``Window`` is a ``tkinter.Tk`` and its widgets are ttk widgets.

.. note::

   The same applies to `bootstack <https://github.com/israel-dryer/bootstack>`_, which also has Bootstrap icons built in.

The basics
----------

.. code-block:: python

   import ttkbootstrap as ttk

   from tkinter_icons import LucideIcon

   app = ttk.Window(themename="darkly")

   save = LucideIcon("save", size=16, color="white")
   ttk.Button(app, text="Save", image=save.image, compound="left").pack(padx=20, pady=20)

   app.mainloop()

That works, and it has a maintenance problem: the color is hard-coded. Switch to a light theme and the icon stays white.

Let the theme pick the color
----------------------------

:meth:`Icon.map <tkinter_icons.Icon.map>` renders the icon once per widget state in the color that widget's style already uses, so a ``success``-styled button gets a green icon without you naming green:

.. code-block:: python

   import ttkbootstrap as ttk

   from tkinter_icons import LucideIcon

   app = ttk.Window(themename="darkly")

   icon = LucideIcon("check", size=16)
   button = ttk.Button(app, text="Approve", bootstyle="success")
   button.pack(padx=20, pady=20)

   icon.map(button)

   app.mainloop()

The icon now follows the button through hover, pressed, and disabled — and re-renders when the theme changes, because ttkbootstrap emits ``<<ThemeChanged>>`` and mapped icons listen for it:

.. code-block:: python

   app.style.theme_use("flatly")     # icons recolor themselves

See :doc:`../guide/stateful-icons` for per-state colors and per-state icon names.

Bootstyle colors
----------------

When you do want to name a color, read it from the theme rather than writing a hex value that only suits one theme:

.. code-block:: python

   colors = app.style.colors

   LucideIcon("check", size=16, color=colors.success)
   LucideIcon("x", size=16, color=colors.danger)
   LucideIcon("info", size=16, color=colors.info)

These are the same tokens ``bootstyle`` uses, so the icon matches the widget beside it in every theme.

Alongside Bootstrap icons
-------------------------

Nothing stops you using ttkbootstrap's built-in Bootstrap icons and a pack from here in the same window. They are separate systems that both end up as Tk images, and each icon here holds its own icon set, so nothing collides.

A common reason to mix: Bootstrap for interface chrome, ``[simple]`` for brand marks that no UI set has.

.. code-block:: bash

   pip install "tkinter-icons[simple]"

.. code-block:: python

   from tkinter_icons import SimpleIcon

   github = SimpleIcon("github", size=16, color="white")
   ttk.Button(app, text="Sign in with GitHub", image=github.image, compound="left").pack()

Which library draws your icon?
------------------------------

.. list-table::
   :header-rows: 1
   :widths: 34 33 33

   * - You want
     - Use
     - Install
   * - Bootstrap icons in ttkbootstrap
     - ttkbootstrap's own
     - nothing extra
   * - Another set in ttkbootstrap
     - this library
     - ``"tkinter-icons[<pack>]"``
   * - Any set in plain tkinter
     - this library
     - ``"tkinter-icons[<pack>]"``

Migrating from ttkbootstrap-icons
---------------------------------

If you arrived from the old ``ttkbootstrap-icons`` package, your imports still work through a shim and the move is two lines. See :ref:`migrating`.