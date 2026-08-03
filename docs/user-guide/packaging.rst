Packaging an application
========================

Icons are font files and JSON living inside installed packages. Freezing tools find code by following imports, and data only by being told about it — so a frozen application that looked correct in development can start up with no icons at all, and start up *quietly*, since a glyph the renderer cannot find draws as transparent.

This package ships PyInstaller hooks that collect that data, and registers them so PyInstaller finds them.

PyInstaller
-----------

There is nothing to configure:

.. code-block:: bash

   pip install pyinstaller
   pyinstaller --onefile your_app.py

The hooks are registered through PyInstaller's ``pyinstaller40`` entry point, so it discovers them itself and collects the font and glyph map of every pack you have installed. A pack you did not install has nothing to collect and is skipped.

.. versionadded:: 5.0.0
   The hooks are registered for automatic discovery. They shipped in earlier versions but nothing pointed PyInstaller at them, so a frozen application needed an explicit ``hookspath`` to get its fonts. Two packs — ``[bootstrap]`` and ``[fluent-regular]`` — also had no hook at all.

Pointing at the hooks explicitly
--------------------------------

Automatic discovery needs the entry point to be visible, which it is for any normal install. If you are vendoring the package, running from a source tree that was never installed, or building with a tool that ignores entry points, name the directory yourself:

.. code-block:: python

   # your_app.spec
   from tkinter_icons import get_hook_dirs

   a = Analysis(
       ["your_app.py"],
       hookspath=get_hook_dirs(),
       ...
   )

Or on the command line:

.. code-block:: bash

   pyinstaller --additional-hooks-dir "$(python -c 'import tkinter_icons; print(tkinter_icons.get_hook_dirs()[0])')" your_app.py

:func:`~tkinter_icons.get_hook_dirs` returns the directory holding every hook — one for the base package and one per pack.

What the hooks do
-----------------

Each is one line of ``collect_data_files`` for its package. That is all that is needed: the font and the glyph map are package data, and once collected the renderer finds them through ``importlib.resources`` exactly as it does from an ordinary install.

Check the build
---------------

Missing data shows up only in the frozen application, and it shows up as absence rather than as an error. Run it:

.. code-block:: bash

   ./dist/your_app        # Linux, macOS
   .\dist\your_app.exe    # Windows

If icons are missing, check that the pack is installed in the environment you built *from*. To turn the silence into a failure while you debug, make a missing glyph raise:

.. code-block:: python

   from tkinter_icons import Icon

   Icon.on_missing = "raise"

Keeping the bundle small
------------------------

An icon font ships every glyph it has, and there is no tree-shaking — the font is one file, so using four icons from a pack costs the same as using four thousand.

The lever is therefore which packs you install. ``[material]`` and ``[fluent]`` are large sets and large files; ``[lucide]`` and ``[bootstrap]`` are a fraction of the size and cover ordinary application needs. Choosing a smaller pack is the whole optimisation.

.. tip::

   This is also why there is no ``[all]`` extra: it would put roughly 22 MB of fonts and glyph data into every bundle to supply icon sets the application never draws.

Other freezers
--------------

cx_Freeze, Nuitka, and py2app do not read PyInstaller hooks, so each pack's data has to be listed explicitly. What a pack needs is its font directory and its JSON:

.. code-block:: python

   # cx_Freeze, in setup.py
   from importlib.resources import files

   pack = files("tkinter_icons_mat")
   include_files = [(str(pack), "lib/tkinter_icons_mat")]

Verify by running the frozen application rather than by reading the configuration. The failure mode is silent.