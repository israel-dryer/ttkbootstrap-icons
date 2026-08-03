API reference
=============

Everything an application needs is importable from ``tkinter_icons``. The machinery for *defining* an icon set — providers and the registry — is a developer API and lives in :doc:`about/contributing`.

.. currentmodule:: tkinter_icons

Icons
-----

.. autoclass:: Icon
   :members:
   :inherited-members:
   :member-order: groupwise

.. autofunction:: create_transparent_icon

Pack icon classes
-----------------

Each pack exports one class, and each of them is a subclass of :class:`Icon` adding nothing but name resolution. The constructor is the same everywhere:

.. code-block:: python

   PackIcon(name: str, size: int = 24, color: str = "black", style: str | None = None)

``style`` is accepted only by packs that have styles; the rest take three arguments. Both spellings of every class are exported — ``MaterialIcon`` and ``MatIcon``, ``FontAwesomeIcon`` and ``FAIcon``, ``GoogleMaterialIcon`` and ``GMatIcon`` — so code written against either keeps working. :doc:`packs` lists them.

Rendering
---------

.. autoclass:: RenderOptions
   :members:

.. autofunction:: render_glyph

.. autofunction:: measure_ink_bounds

Icon sets
---------

.. autoclass:: IconSet
   :members:

.. autofunction:: get_icon_set

Packs
-----

.. autoclass:: Pack
   :members:

.. autodata:: KNOWN_PACKS
   :no-value:

.. autofunction:: find_pack

.. autofunction:: installed_packs

Packaging
---------

.. autofunction:: get_hook_dirs