Installation
============

Icons come from packs, and a pack is installed as an extra:

.. code-block:: bash

   pip install "tkinter-icons[material]"

The quotes matter. Most shells treat unquoted brackets as a glob pattern, and zsh fails outright on ``pip install tkinter-icons[material]``.

Need more than one set? Name them together:

.. code-block:: bash

   pip install "tkinter-icons[material,simple]"

:doc:`choosing-a-pack` covers which one to reach for; :doc:`../packs` is the full catalogue with sizes, styles, and upstream versions.

The base package draws nothing
------------------------------

.. important::

   Every install line in this documentation carries an extra, and that is deliberate. ``pip install tkinter-icons`` gives you a working renderer with no glyphs — asking for an icon class then raises an :class:`ImportError` naming the command you actually wanted.

The split exists because each pack ships its own font. Bundling all sixteen would cost roughly 17 MB to supply fifteen icon sets an application never opens, so they are separate distributions — presented as extras so you install one library rather than learning sixteen distribution names.

.. warning::

   There is no ``[all]`` extra, and there will not be one. The sixteen sets serve unrelated purposes — brand marks, developer logos, fantasy glyphs, weather symbols — so no application draws from all of them. Name the ones you use.

Requirements
------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Requirement
     - Notes
   * - Python 3.10+
     - Tested on 3.10 through 3.13.
   * - Tk 8.6+
     - Ships with CPython on Windows and macOS.
   * - Pillow
     - Installed for you; it is what does the rendering.

On Linux, Tk usually comes from your distribution rather than from pip:

.. code-block:: bash

   sudo apt install python3-tk        # Debian, Ubuntu
   sudo dnf install python3-tkinter   # Fedora

You do **not** need a display to render icons — :doc:`../user-guide/headless-rendering` covers using the library with no Tk at all.

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
