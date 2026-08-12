Icon browser
============

Icon names are impossible to guess and tedious to look up on sixteen different websites, so the base package ships a browser:

.. code-block:: bash

   tkinter-icons

.. image:: /assets/browser.png
   :alt: The icon browser, showing a searchable grid of icons with a detail panel
   :class: window-screenshot

It lists every pack you have installed, in one window.

What it gives you
-----------------

**Search**, across the names in the selected set. Type ``arrow`` and see every arrow.

**Style switching**, for packs that have styles — the same icon as outline and fill, side by side in practice.

**Size and color**, so you can see an icon at the size you will actually use it rather than at a comfortable preview size. A glyph that reads well at 48 px can turn to mush at 16.

**The name, and a Copy button.** This is the point of the whole thing. The name it copies is the one to pass to the icon class.

**The Unicode codepoint**, and links to the upstream project and its license.

Only one pack installed? The browser still opens on it. None installed? It says so, and lists the install commands.

Running it another way
----------------------

The console script is the ordinary route, but the module works too — handy inside a virtual environment whose scripts are not on ``PATH``:

.. code-block:: bash

   python -m tkinter_icons.browser

Or embed it, if you want an icon picker inside your own tooling:

.. code-block:: python

   import tkinter as tk

   from tkinter_icons.browser import IconPreviewerApp

   root = tk.Tk()
   IconPreviewerApp(root)
   root.mainloop()

.. note::

   ``tkinter-icons`` is the only command this package installs. The asset-building commands earlier versions put on your ``PATH`` are gone — see :doc:`../getting-started/migrating` for why, and :doc:`../about/contributing` for how maintainers run them now.