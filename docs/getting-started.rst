Getting started
===============

Install
-------

Pick an icon pack and install it as an extra:

.. code-block:: bash

   pip install "tkinter-icons[material]"

The quotes matter. Most shells treat unquoted brackets as a glob pattern, and zsh fails outright on ``pip install tkinter-icons[material]``.

Need more than one set? Name them together:

.. code-block:: bash

   pip install "tkinter-icons[material,simple]"

Requirements are Python 3.10 or newer, Tk 8.6 or newer, and Pillow — which pip installs for you. On Linux, Tk itself usually comes from your distribution rather than pip: ``sudo apt install python3-tk`` on Debian and Ubuntu.

.. warning::

   There is no ``[all]`` extra, and there will not be one. The sixteen sets serve unrelated purposes — brand marks, developer logos, fantasy glyphs, weather symbols — so no application draws from all of them, and installing every one costs about 17 MB of fonts to get fifteen sets nobody opens. Name the ones you use.

Quickstart
----------

.. code-block:: python

   import tkinter as tk
   from tkinter import ttk

   from tkinter_icons import MaterialIcon

   root = tk.Tk()

   home = MaterialIcon("home", size=24, color="#0d6efd")
   ttk.Button(root, text="Home", image=home.image, compound="left").pack(padx=20, pady=20)

   root.mainloop()

Three things are happening here, and each of them matters later.

**The class comes from the pack you installed.** ``MaterialIcon`` is re-exported from ``tkinter_icons`` even though it lives in the ``tkinter-icons-mat`` distribution, so the name you install is the name you import. Asking for a class from a pack you have not installed raises an :class:`ImportError` that names the exact command to fix it.

**Constructing an icon draws nothing.** :class:`~tkinter_icons.Icon` never touches Tk in its constructor; the image is rendered the first time you read :attr:`~tkinter_icons.Icon.image`. You can build icons at import time, in a config object, or before there is a root window.

**Keep a reference.** This is a Tk rule rather than one of ours: a ``PhotoImage`` that nothing refers to is garbage collected, and the widget shows an empty box. Holding the icon object — in a variable, an attribute, a list — is enough, because it holds the image.

.. code-block:: python

   # Wrong: nothing holds the icon, so nothing holds its image.
   ttk.Button(root, image=MaterialIcon("home").image).pack()

   # Right: the icon lives as long as the object holding it.
   self.home = MaterialIcon("home")
   ttk.Button(root, image=self.home.image).pack()

Choosing a pack
---------------

:doc:`packs` compares all sixteen with their sizes, styles, and upstream versions. If you have no particular preference:

* **A general-purpose UI set** — ``[material]`` (14,000+ icons), ``[lucide]``, or ``[bootstrap]``.
* **Font Awesome**, if that is the vocabulary you already think in — ``[fontawesome]``, which brings solid, regular, and brand styles.
* **Brand and product marks** — ``[simple]`` for 3,000+ company logos, ``[devicon]`` for developer tooling.
* **Something specific** — ``[weather]`` and ``[meteocons]`` for forecasts, ``[rpg-awesome]`` for games.

You are not locked in. Every pack's icon class takes the same arguments, so trying another set is an install and a one-line change.

.. code-block:: python

   from tkinter_icons import LucideIcon as Icon   # was: MaterialIcon as Icon

Not sure what an icon is called? The browser ships with the base package:

.. code-block:: bash

   tkinter-icons

It shows every installed set, searchable, with the exact name to copy. See :doc:`guide/icon-browser`.

.. _migrating:

Migrating from ttkbootstrap-icons
---------------------------------

This project was ``ttkbootstrap-icons`` through 4.0.0. The name promised a relationship with ttkbootstrap that no longer holds — Bootstrap icons are now built directly into both ttkbootstrap and bootstack — so 5.0.0 renamed it to ``tkinter-icons``.

**Your existing code keeps working.** ``ttkbootstrap-icons`` 5.0.0 is a forwarding shim: it depends on ``tkinter-icons`` and re-exports everything, including submodules, so ``from ttkbootstrap_icons.icon import Icon`` still resolves. It warns once on import and will not be updated again.

To move over:

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - 4.0.0
     - 5.0.0
   * - ``pip install ttkbootstrap-icons``
     - ``pip install "tkinter-icons[bootstrap]"``
   * - ``pip install ttkbootstrap-icons-mat``
     - ``pip install "tkinter-icons[material]"``
   * - ``from ttkbootstrap_icons import Icon``
     - ``from tkinter_icons import Icon``
   * - ``from ttkbootstrap_icons_mat import MatIcon``
     - ``from tkinter_icons import MaterialIcon``

Both spellings of every class are exported, so ``MatIcon``, ``FAIcon``, and ``GMatIcon`` still resolve from ``tkinter_icons`` alongside the spelled-out ``MaterialIcon``, ``FontAwesomeIcon``, and ``GoogleMaterialIcon``.

Two things genuinely changed:

**The base package no longer bundles Bootstrap icons.** That happened in 4.0.0, not in the rename. If you were relying on it, install ``"tkinter-icons[bootstrap]"``.

**Icons render slightly differently**, because 5.0.0 centers them on measured ink rather than on Pillow's ``getbbox``. Full-bleed glyphs gain the padding they were missing, and everything else sits a little more centered. If you had compensated for the old behaviour with your own padding, take it back out. See :doc:`guide/sizing-and-quality`.

Where to next
-------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Icons and names
      :link: guide/icons-and-names
      :link-type: doc

      How names resolve, what styles are, and what happens when a name is wrong.

   .. grid-item-card:: Sizing and render quality
      :link: guide/sizing-and-quality
      :link-type: doc

      Sizes, padding, sharpness, and the knobs on ``RenderOptions``.

   .. grid-item-card:: Stateful icons
      :link: guide/stateful-icons
      :link-type: doc

      Icons that follow a widget's hover, pressed, and disabled colors.

   .. grid-item-card:: Icon packs
      :link: packs
      :link-type: doc

      All sixteen sets, compared.