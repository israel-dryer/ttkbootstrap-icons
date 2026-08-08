Icons and names
===============

An icon is a description, not a picture
---------------------------------------

Creating an icon costs almost nothing. The constructor resolves the name, records the size and color, and stops — it does not open Tk, allocate an image, or touch a display:

.. code-block:: python

   from tkinter_icons import MaterialIcon

   home = MaterialIcon("home", size=24, color="#0F766E")   # nothing drawn yet
   home.image                                              # drawn here

That is why icons can be built before there is a root window, kept in a module-level table, or passed around as configuration. It is also why the same icon costs nothing twice: two icons with the same set, name, size, color, and options share one rendered image.

.. code-block:: python

   MaterialIcon("home", 24, "black").image is MaterialIcon("home", 24, "black").image
   # True - one image, cached per Tk interpreter

Naming
------

Names are the upstream project's own, lowercase and hyphenated:

.. code-block:: python

   MaterialIcon("account-circle")
   LucideIcon("chevron-right")
   BootstrapIcon("file-earmark-text")

If you are guessing, don't — run ``tkinter-icons`` and search. See :doc:`icon-browser`.

Styles
------

Some packs draw the same icon several ways. Bootstrap has ``outline`` and ``fill``; Font Awesome has ``solid``, ``regular``, and ``brands``; Google Material has four. A pack with styles takes a ``style`` argument, and you can also carry the style in the name:

.. code-block:: python

   from tkinter_icons import BootstrapIcon

   BootstrapIcon("house", style="fill")
   BootstrapIcon("house-fill")             # equivalent

When both are given and they disagree, that is an error rather than a silent preference:

.. code-block:: python

   BootstrapIcon("house-fill", style="outline")
   # ValueError: 'house-fill' is not valid for style 'outline' in bootstrap.
   #             Try style 'fill' or use an unsuffixed name.

Omit ``style`` and the pack uses its default — ``outline`` for Bootstrap, ``solid`` for Font Awesome. The Styles column on :doc:`../packs` lists what each pack accepts; several packs have none and take no ``style`` argument at all.

A style is a different drawing of the same idea, not a different icon. Bootstrap's two, on the same six names:

.. pack-preview:: bootstrap

When a name is wrong
--------------------

The same bad name fails two different ways, depending on which entry point you reached it through.

**The pack's constructor raises**, immediately:

.. code-block:: python

   MaterialIcon("hoome")
   # ValueError: hoome not found in lookup for mat in fill style.

**Everything that draws applies a policy instead.** :meth:`~tkinter_icons.Icon.render_pil` swallows the same failure on purpose: it is the headless path, usually writing a whole sheet of images at once, where one unusable name should not take the rest down with it. The base :class:`~tkinter_icons.Icon` never resolves at all — it takes an already-resolved glyph name and trusts it. ``on_missing`` is what both do when the set cannot draw the name they were handed, and by default that is a transparent square:

.. code-block:: python

   from tkinter_icons import Icon

   Icon.on_missing = "raise"     # or "warn", or the default "transparent"

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Value
     - Behavior
   * - ``"transparent"``
     - Draw an empty square of the right size. The default.
   * - ``"warn"``
     - Draw the empty square and emit a :class:`UserWarning`.
   * - ``"raise"``
     - Raise :class:`KeyError`.

Since the constructor is the only thing that raises of its own accord, ``"warn"`` is what turns a silently blank square back into something you can see. It suits a test suite: nothing breaks, but nothing passes silently either.

Asking for a pack you have not installed
----------------------------------------

The import root knows all sixteen packs whether or not they are installed, so this fails with instructions rather than a bare :class:`ImportError` about a module you never named:

.. code-block:: python

   from tkinter_icons import WeatherIcon
   # ImportError: The Weather Icons pack is not installed.
   #
   #   pip install "tkinter-icons[weather]"
   #
   # Then: from tkinter_icons import WeatherIcon
   #
   # Currently installed: material, simple

Inspecting what you have
------------------------

The pack catalog is importable, which is useful in a diagnostics screen or a test that asserts what an environment carries:

.. code-block:: python

   from tkinter_icons import installed_packs, find_pack

   for pack in installed_packs():
       print(pack.extra, pack.label, pack.import_statement)

   find_pack("mat")                  # by provider name, extra, module, or distribution
   find_pack("tkinter-icons-mat")

What an icon knows about itself
-------------------------------

.. code-block:: python

   icon = MaterialIcon("home", size=15)

   icon.name             # 'home' - the resolved glyph name
   icon.size             # 15 - what you asked for
   icon.rendered_size    # 16 - what was drawn; odd sizes snap up
   icon.icon_set         # the IconSet it draws from
   icon.icon_set.id      # 'mat:default'
   len(icon.icon_set)    # how many glyphs that set has
   "home" in icon.icon_set

:attr:`~tkinter_icons.Icon.rendered_size` is worth knowing if you are laying out around an icon — see :doc:`sizing-and-quality`.