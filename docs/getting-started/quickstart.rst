Quickstart
==========

.. code-block:: python

   import tkinter as tk
   from tkinter import ttk

   from tkinter_icons import MaterialIcon

   root = tk.Tk()

   home = MaterialIcon("home", size=24, color="#0d6efd")
   ttk.Button(root, text="Home", image=home.image, compound="left").pack(padx=20, pady=20)

   root.mainloop()

Three things are happening there, and each of them matters later.

The class comes from the pack you installed
-------------------------------------------

``MaterialIcon`` is re-exported from ``tkinter_icons`` even though it lives in the ``tkinter-icons-mat`` distribution, so **the name you install is the name you import**. Every pack works this way, and both spellings resolve — ``MaterialIcon`` and ``MatIcon``, ``FontAwesomeIcon`` and ``FAIcon``.

Asking for a class from a pack you have not installed does not fail obscurely:

.. code-block:: python

   from tkinter_icons import WeatherIcon
   # ImportError: The Weather Icons pack is not installed.
   #
   #   pip install "tkinter-icons[weather]"
   #
   # Then: from tkinter_icons import WeatherIcon

Constructing an icon draws nothing
----------------------------------

:class:`~tkinter_icons.Icon` never touches Tk in its constructor. The image is rendered the first time you read :attr:`~tkinter_icons.Icon.image`, so icons can be built at import time, kept in a configuration object, or created before a root window exists.

.. code-block:: python

   ICONS = {                                  # module level, before tk.Tk()
       "save": MaterialIcon("content-save", size=16),
       "open": MaterialIcon("folder-open", size=16),
   }

Identical icons share one image, so building the same icon twice costs nothing.

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

- :doc:`../user-guide/icons-and-names` — how names resolve, and what styles are
- :doc:`../user-guide/stateful-icons` — icons that follow a widget's hover and disabled colors
- :doc:`choosing-a-pack` — if ``[material]`` is not the set you want
