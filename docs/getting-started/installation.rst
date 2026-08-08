Installation
============

Icons come from packs, and a pack is installed as an extra:

.. code-block:: bash

   pip install "tkinter-icons[material]"

The quotes matter. Most shells treat unquoted brackets as a glob pattern, and zsh fails outright on ``pip install tkinter-icons[material]``.

Need more than one set? Name them together:

.. code-block:: bash

   pip install "tkinter-icons[material,simple]"

:doc:`choosing-a-pack` covers which one to reach for; :doc:`../packs` is the full catalog with sizes, styles, and upstream versions.

The base package draws nothing
------------------------------

.. important::

   Every install line in this documentation carries an extra, and that is deliberate. ``pip install tkinter-icons`` gives you a working renderer with no glyphs — asking for an icon class then raises an :class:`ImportError` naming the command you actually wanted.

The split exists because each pack ships its own font. Bundling all sixteen would cost roughly 22 MB to supply fifteen icon sets an application never opens, so they are separate distributions — presented as extras so you install one library rather than learning sixteen distribution names.

.. warning::

   There is no ``[all]`` extra, and asking for one fails quietly. pip does not treat an unknown extra as an error, so ``pip install "tkinter-icons[all]"`` reports success and installs the base package — leaving you exactly where the note above says you do not want to be, with no indication that anything was ignored. Name the sets you use.

:doc:`../packs` covers why there is no ``[all]`` and never will be.

Requirements
------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Requirement
     - Notes
   * - Python 3.10+
     - Tested on 3.10 through 3.14.
   * - Tk 8.6+
     - Ships with CPython on Windows and macOS.
   * - Pillow
     - Installed for you; it is what does the rendering.

On Linux, Tk usually comes from your distribution rather than from pip:

.. code-block:: bash

   sudo apt install python3-tk        # Debian, Ubuntu
   sudo dnf install python3-tkinter   # Fedora

You do **not** need a display to render icons. Tk still has to be installed, but nothing has to be shown — :doc:`../user-guide/headless-rendering` covers rendering with no display, no root window, and no event loop.

Checking what you have
----------------------

.. code-block:: python

   from tkinter_icons import installed_packs

   for pack in installed_packs():
       print(pack.extra, "-", pack.label)

.. code-block:: text

   material - Material Design Icons
   simple - Simple Icons

Or run the browser, which lists every installed set:

.. code-block:: bash

   tkinter-icons
