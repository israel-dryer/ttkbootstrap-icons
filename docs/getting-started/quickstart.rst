Quickstart
==========

.. code-block:: python

   import tkinter as tk
   from tkinter import ttk

   from tkinter_icons import MaterialIcon

   root = tk.Tk()

   home = MaterialIcon("home", size=24, color="#0F766E")
   ttk.Button(root, text="Home", image=home.image, compound="left").pack(padx=20, pady=20)

   root.mainloop()

.. image:: /assets/quickstart_button.png
   :alt: A small window with one button reading Home, a teal house icon to the left of the text

That is the shape of every icon in every pack: a name, a size, a color, and ``.image`` where a widget wants a picture. Three things trip people up first, and they are the rest of this page.

Every pack imports from ``tkinter_icons``
-----------------------------------------

Whichever pack you installed, its class comes from the same place — ``LucideIcon``, ``FontAwesomeIcon``, ``WeatherIcon``, all from ``tkinter_icons``. Switching sets is a one-line change.

Ask for a pack you have not installed and you get instructions rather than a puzzle:

.. code-block:: python

   from tkinter_icons import WeatherIcon
   # ImportError: The Weather Icons pack is not installed.
   #
   #   pip install "tkinter-icons[weather]"
   #
   # Then: from tkinter_icons import WeatherIcon

Keep a reference
----------------

This is a Tk rule rather than one of ours: a ``PhotoImage`` that nothing refers to is garbage collected, and the widget shows an empty box. Holding the icon object is enough, because it holds the image.

.. code-block:: python

   # Wrong: nothing holds the icon, so nothing holds its image.
   ttk.Button(root, image=MaterialIcon("home").image).pack()

   # Right: the icon lives as long as the object holding it.
   self.home = MaterialIcon("home")
   ttk.Button(root, image=self.home.image).pack()

It catches everyone once. :doc:`../integrations/tkinter-ttk` has the same rule stated where it usually bites — menus and trees, which outlive the function that built them.

Finding icon names
------------------

Names are the upstream project's own, and not always the word you would pick — Material Design Icons calls the gear ``cog``, not ``settings``. Rather than guess, run the browser:

.. code-block:: bash

   tkinter-icons

It shows every installed set, searchable, at the size and color you will actually use, with a button that copies the name. See :doc:`../user-guide/icon-browser`.

Next
----

- :doc:`../user-guide/icons-and-names` — what an icon actually is, how names resolve against styles, and why building one costs nothing
- :doc:`../user-guide/stateful-icons` — icons that follow a widget's hover and disabled colors
- :doc:`choosing-a-pack` — if ``[material]`` is not the set you want
