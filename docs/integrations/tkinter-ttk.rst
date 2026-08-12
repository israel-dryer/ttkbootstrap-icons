tkinter and ttk
===============

An icon's :attr:`~tkinter_icons.Icon.image` is an ordinary Tk-compatible image, so anything with an ``image`` option takes one. Nothing here is special to this library — it is the ordinary Tk API, written down in one place.

.. image:: /assets/tkinter_ttk_widgets.png
   :alt: A ttk window with a File menubar, a Save button, an icon-only close button, a labelled folder, and a treeview whose rows carry folder and document icons
   :class: window-screenshot

Everything below is in that window: the buttons and label across the top, the menu behind ``File``, and the treeview under both.

.. important::

   **Keep a reference to the icon.** Tk does not own the images you give it; a ``PhotoImage`` that nothing refers to is garbage collected and the widget shows an empty box. Holding the icon object is enough, since it holds the image. This catches everyone once.

Buttons and labels
------------------

``compound`` decides where the image sits relative to the text:

.. code-block:: python

   import tkinter as tk
   from tkinter import ttk

   from tkinter_icons import LucideIcon

   root = tk.Tk()

   self_save = LucideIcon("save", size=16, color="#212529")
   ttk.Button(root, text="Save", image=self_save.image, compound="left").pack()

   ttk.Label(root, text="Documents", image=self_save.image, compound="top").pack()

Icon-only buttons pass no text at all:

.. code-block:: python

   close = LucideIcon("x", size=16)
   ttk.Button(root, image=close.image, width=3).pack()

Menus
-----

Menu entries take ``image`` and ``compound`` the same way. Menus are a common place to lose an image to garbage collection, because the menu outlives the function that built it — keep the icons on the object that owns the menu:

.. code-block:: python

   class App:
       def __init__(self, root):
           self.icons = {
               "new": LucideIcon("file-plus", size=16),
               "open": LucideIcon("folder-open", size=16),
               "quit": LucideIcon("log-out", size=16),
           }

           menu = tk.Menu(root)
           file_menu = tk.Menu(menu, tearoff=False)
           file_menu.add_command(label="New", image=self.icons["new"].image, compound="left")
           file_menu.add_command(label="Open", image=self.icons["open"].image, compound="left")
           file_menu.add_separator()
           file_menu.add_command(label="Quit", image=self.icons["quit"].image, compound="left")
           menu.add_cascade(label="File", menu=file_menu)
           root.config(menu=menu)

Treeview
--------

A ``Treeview`` takes one image per row, which is how you get a file tree with type icons:

.. code-block:: python

   tree = ttk.Treeview(root, columns=("size",))
   tree.pack(fill="both", expand=True)

   folder = LucideIcon("folder", size=16, color="#f0ad4e")
   document = LucideIcon("file-text", size=16, color="#6c757d")

   src = tree.insert("", "end", text="src", image=folder.image, open=True)
   tree.insert(src, "end", text="main.py", image=document.image, values=("2.1 kB",))

Notebook tabs
-------------

.. code-block:: python

   notebook = ttk.Notebook(root)
   settings = LucideIcon("settings", size=16)
   notebook.add(page, text="Settings", image=settings.image, compound="left")

The window icon
---------------

``iconphoto`` wants a larger image than the interface uses, and it is the one place where turning padding off is usually right — the icon is alone in its frame rather than sitting beside text:

.. code-block:: python

   from tkinter_icons import LucideIcon, RenderOptions

   mark = LucideIcon("zap", size=64, color="#0F766E",
                     options=RenderOptions(pad_factor=0.0, align=True))
   root.iconphoto(True, mark.image)

Canvas
------

.. code-block:: python

   canvas = tk.Canvas(root, width=400, height=300)
   canvas.pack()

   pin = LucideIcon("map-pin", size=24, color="#dc3545")
   canvas.create_image(120, 80, image=pin.image)

The same icon object can be placed many times — one image, drawn wherever you put it.

Sizing icons against text
-------------------------

Icon size is in pixels, font size usually in points, so they do not line up by default. A reasonable rule is to match the icon to the font's pixel height:

.. code-block:: python

   import tkinter.font as tkfont

   font = tkfont.nametofont("TkDefaultFont")
   size = font.metrics("linespace")            # pixels, scaling-aware

   icon = LucideIcon("info", size=size, color="#0F766E")

``linespace`` already accounts for display scaling, so this stays right on a 150% display where a hard-coded 16 would not.

Following a theme
-----------------

Everything above pins a color. For icons that recolor themselves as the widget changes state — and again when the theme changes — see :doc:`../user-guide/stateful-icons`.