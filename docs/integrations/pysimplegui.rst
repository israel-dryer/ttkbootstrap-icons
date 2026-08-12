PySimpleGUI
===========

`PySimpleGUI <https://github.com/PySimpleGUI/PySimpleGUI>`_ builds a window from a layout you write as a list of lists. That declarative style is the whole reason it needs an integration: constructing ``sg.Button`` creates no Tk widget at all, so at the moment you write your layout there is no widget to put an icon on, and no Tk interpreter to render one with.

There are two ways in, and they are not interchangeable.

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: :class:`~tkinter_icons.extensions.psg.IconButton`

      For an icon **beside text**, or one that has to react to hover, press and disable. Applies itself once the window is built.

   .. grid-item-card:: :meth:`Icon.to_data <tkinter_icons.Icon.to_data>`

      For anything that takes an encoded image — ``sg.Image``, ``sg.Tab``, the window icon, icon-only buttons. Bytes, so no deferral and no subclass.

.. figure:: ../assets/pysimplegui_icons.png
   :alt: A PySimpleGUI window with icon buttons and image elements, all drawn from icon fonts.
   :align: center

   Both bridges in one window. The top row is :class:`~tkinter_icons.extensions.psg.IconButton` — Delete is shown disabled, and swaps to a filled glyph to say so. The bottom row is ``to_data()`` bytes on an ``sg.Image`` and an icon-only ``sg.Button``.

Installing
----------

PySimpleGUI is **not** a dependency of ``tkinter-icons`` and nothing from it is redistributed here. Install it yourself, alongside whichever icon packs you want:

.. code-block:: shell

   pip install "tkinter-icons[bootstrap]" PySimpleGUI

Either flavor works — PySimpleGUI, LGPL v3 as of version 6, or `FreeSimpleGUI <https://github.com/spyoungtech/FreeSimpleGUI>`_, the LGPL fork of the 4.x line. The integration uses only the parts they share.

.. important::

   **Import your GUI framework before this integration.** :class:`~tkinter_icons.extensions.psg.IconButton` subclasses the flavor's own ``Button``, so it has to know which one you are using. It looks at what you have already imported, which is why import order matters when both are installed:

   .. code-block:: python

      import PySimpleGUI as sg                             # first
      from tkinter_icons.extensions.psg import IconButton  # then this

   Getting it backwards is caught rather than left to produce something strange later: building a layout that mixes the two raises and names both.

Buttons
-------

.. code-block:: python

   import PySimpleGUI as sg

   from tkinter_icons import BootstrapIcon
   from tkinter_icons.extensions.psg import IconButton

   layout = [
       [IconButton("Save", icon=BootstrapIcon("floppy", 16, "#FFFFFF"), key="-SAVE-")],
       [IconButton("", icon=BootstrapIcon("gear", 16, "#FFFFFF"), key="-PREFS-")],
   ]

   window = sg.Window("Editor", layout, finalize=True)

Building the icon inline costs nothing — an :class:`~tkinter_icons.Icon` renders on demand, not on construction — and the icon is applied for you when the window is built, before it is drawn.

Reacting to the button
----------------------

By default the icon follows the button's own colors, so it greys out with the label when the button is disabled and picks up whatever colors your theme gave it. Pass ``reactive_states`` to say more:

.. code-block:: python

   IconButton(
       "Delete",
       icon=BootstrapIcon("trash", 16, "#FFFFFF"),
       reactive_states={
           "hover": "#f0918d",
           "pressed": "#d9534f",
           "disabled": {"name": "trash-fill", "color": "#7c8a99"},
       },
       key="-DELETE-",
       use_ttk_buttons=True,
   )

A state maps to a color, or to a dict that can swap the glyph as well — the disabled state above changes to the filled trash so the button reads differently even in grey. Pass ``reactive_states=False`` to draw the icon exactly as you constructed it and ignore the button entirely.

.. _psg-states:

The states are named for the interaction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``hover``, ``pressed`` and ``disabled`` describe what the user is doing, not what either toolkit calls it — and the two toolkits disagree, which is why the names could not simply be borrowed. In ttk, ``active`` means the pointer is over the widget. On a plain ``tk.Button``, ``active`` means *pressed*: Tk sets that state only while the mouse button is already down.

That difference is not cosmetic, because a ``tk.Button`` has **no hover state that can carry an image** at all. Hover is drawn there with ``-overrelief``, and a relief is not a picture. So:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - State
     - ttk button
     - tk button
   * - ``hover``
     - the pointer is over the button
     - **unavailable** — asking for it warns
   * - ``pressed``
     - the button is held down
     - the button is held down
   * - ``disabled``
     - the button is disabled
     - the button is disabled

Pass ``use_ttk_buttons=True`` — on the button or on the window — to get all three. PySimpleGUI defaults to ``tk`` buttons on Windows and Linux.

Changing the icon later
-----------------------

``update()`` takes everything the constructor does, so one element can carry two glyphs:

.. code-block:: python

   playing = False
   while True:
       event, values = window.read()
       if event == sg.WINDOW_CLOSED:
           break
       if event == "-PLAY-":
           playing = not playing
           name = "pause-fill" if playing else "play-fill"
           window["-PLAY-"].update(icon=BootstrapIcon(name, 16, "#FFFFFF"))

``update(compound=...)`` moves the icon relative to the text, and ``update(reactive_states=...)`` changes the state behavior. The ordinary PySimpleGUI arguments work as they always did, and two of them are followed automatically: ``update(disabled=True)`` swaps to the disabled glyph, and ``update(button_color=...)`` re-tints the icon to match the new colors.

.. note::

   ``sg.theme()`` is **not** followed, because PySimpleGUI does not follow it either — a theme change affects only windows built afterward, and the usual answer is to close the window and build it again. A new window gets correctly colored icons automatically. An icon that chased ``sg.theme()`` would react to something the button under it ignores.

Everything that is not a button
-------------------------------

Most places PySimpleGUI accepts an image, it wants **bytes**. Build the icon exactly as you would for a button and ask it for its data — :meth:`~tkinter_icons.Icon.to_data` needs no Tk root, so it can be called while you are still writing the layout:

.. code-block:: python

   import PySimpleGUI as sg

   from tkinter_icons import BootstrapIcon

   white = "#FFFFFF"

   layout = [
       [sg.Image(data=BootstrapIcon("house", 16, white).to_data()), sg.Text("Dashboard")],
       [sg.Button(image_data=BootstrapIcon("bell", 16, white).to_data(), key="-BELL-")],
       [sg.TabGroup([[
           sg.Tab("Home", [[sg.Text("...")]],
                  image_source=BootstrapIcon("house", 16, white).to_data()),
       ]])],
   ]

   window = sg.Window(
       "Dashboard", layout, finalize=True,
       icon=BootstrapIcon("gear", 32, white).to_data(),
   )

That is the same icon you would hand to :class:`~tkinter_icons.extensions.psg.IconButton`, so there is one idiom on the page rather than two — build an icon, then use it. Constructing one renders nothing until you ask, so it costs no more than the classmethod does.

The same bytes work in ``update()`` at runtime — ``window["-IMG-"].update(data=...)``.

.. tip::

   :meth:`Icon.render_data <tkinter_icons.Icon.render_data>` is the same thing without an instance — ``BootstrapIcon.render_data("house", 16, white)``. Reach for it in library code, or when you want to name an icon set explicitly, which the constructor cannot do.

.. warning::

   ``image_data`` on an ``sg.Button`` is **not** a substitute for :class:`~tkinter_icons.extensions.psg.IconButton`. PySimpleGUI centers the image and sizes the button to it, so any text you also set is drawn *on top of* the icon rather than beside it. Use ``image_data`` for icon-only buttons, and ``IconButton`` when there is a label.

   Bytes are also a snapshot: nothing about them follows the button's state or colors. That is exactly why both bridges exist.

Sizing
------

Give the icon the pixel size you want it drawn at — ``BootstrapIcon("floppy", 16)``, not the button's text size. Two things are worth knowing:

* On a ``tk`` button, an explicit ``size=`` is not honored once an icon is attached. Tk measures a button's width and height in characters while it shows text alone and in **pixels** once it also shows an image, so the size PySimpleGUI set would be reinterpreted and collapse the button. The button is auto-sized instead. ``ttk`` has no such reinterpretation.
* Icons are snapped up to an even pixel size, so ``size=15`` draws at 16. See :doc:`../user-guide/sizing-and-quality`.

.. versionadded:: 5.1.0
   ``tkinter_icons.extensions.psg``.
