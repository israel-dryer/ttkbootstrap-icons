.. _migrating:

Migrating from ttkbootstrap-icons
=================================

This project was published as ``ttkbootstrap-icons`` through 4.0.0. The name promised a relationship with ttkbootstrap that no longer holds — Bootstrap icons are now built directly into `ttkbootstrap <https://github.com/israel-dryer/ttkbootstrap>`_ itself — so 5.0.0 renamed it to ``tkinter-icons``.

**Your existing code keeps working.** ``ttkbootstrap-icons`` 5.0.0 is a forwarding shim: it depends on ``tkinter-icons`` and re-exports everything, submodules included, so ``from ttkbootstrap_icons.icon import Icon`` still resolves. It warns once on import and will not be updated again.

The move
--------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - 4.0.0
     - 5.0.0
   * - ``pip install ttkbootstrap-icons ttkbootstrap-icons-bs``
     - ``pip install "tkinter-icons[bootstrap]"``
   * - ``pip install ttkbootstrap-icons ttkbootstrap-icons-mat``
     - ``pip install "tkinter-icons[material]"``
   * - ``from ttkbootstrap_icons import Icon``
     - ``from tkinter_icons import Icon``
   * - ``from ttkbootstrap_icons_mat import MatIcon``
     - ``from tkinter_icons import MaterialIcon``
   * - ``from ttkbootstrap_icons.registry import ProviderRegistry``
     - ``from tkinter_icons.registry import ProviderRegistry``

Both spellings of every class are exported, so ``MatIcon``, ``FAIcon``, and ``GMatIcon`` still resolve from ``tkinter_icons`` alongside the spelled-out ``MaterialIcon``, ``FontAwesomeIcon``, and ``GoogleMaterialIcon``. Nothing forces you to rename anything beyond the import root.

What genuinely changed
----------------------

**Icons render slightly differently.** 5.0.0 centers glyphs on their measured ink rather than on Pillow's ``getbbox``, which under-reports it. Full-bleed icons gain the padding they were missing, and everything else sits a little more centered. If you compensated for the old behaviour with your own padding or a ``y_bias``, take it back out. :doc:`../user-guide/sizing-and-quality` explains the change.

Also worth knowing
------------------

**Some names left the package root.** ``ProviderRegistry`` and ``load_external_providers`` define an icon set rather than use one, so they moved to ``tkinter_icons.registry``; ``BaseFontProvider`` is in ``tkinter_icons.providers``. The shim still exports all three from its root, so only code that has already switched to ``tkinter_icons`` needs the new paths.

**The asset-building commands are gone.** ``tkicons-build-all``, ``tkicons-metrics``, and the per-pack ``tkicons-<pack>-build`` commands regenerate assets into a source tree, so they did nothing from an installed wheel. ``tkinter-icons`` — the browser — is the only command now. Maintainers run the rest with ``python -m``; see :doc:`../about/contributing`.

**The documentation moved.** The docs now live on Read the Docs at `tkinter-icons.readthedocs.io <https://tkinter-icons.readthedocs.io/en/latest/>`_. The old GitHub Pages sites do not forward — GitHub redirects repository URLs but not project Pages — so both ``israel-dryer.github.io/ttkbootstrap-icons/`` and ``israel-dryer.github.io/tkinter-icons/`` are dead. Update any bookmarks.

When to drop the shim
---------------------

There is no deadline — the shim pins ``tkinter-icons>=5.0.0`` with no upper bound, so it keeps forwarding to every future version. The only reasons to move are the import warning and the fact that new documentation is written against the real name.

The full list of changes is in the :doc:`../about/release-notes`.
