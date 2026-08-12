"""Integrations with GUI frameworks that are not part of this package.

Each module here bridges `tkinter_icons` onto one framework, and each is
optional: the framework is a separate installable that the caller brings, and
nothing in it is redistributed here.

**Nothing in this file may import a submodule.** Importing `tkinter_icons`
pulls this package in, so an import here would give the base package a
load-time dependency on a GUI toolkit it does not declare — for everyone,
including the majority who never touch an integration. `tests/test_extensions.py`
enforces that.

Import the one you want by name::

    from tkinter_icons.extensions.psg import IconButton

.. versionadded:: 5.1.0
"""

from __future__ import annotations

__all__: list[str] = []
