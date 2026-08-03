Fluent System Icons (Regular)
=============================

The regular weight of :doc:`fluent` on its own — the same drawings from the same upstream release, with the filled and light cuts left out.

There is one reason to prefer it: size. The full pack carries three cuts in one font; this one carries the cut most applications actually use. If you are freezing an application (see :doc:`../user-guide/packaging`) and you were never going to use ``filled``, this is most of the coverage at a fraction of the weight.

Take :doc:`fluent` instead if you want a filled state for selection, or if you want the 32px ``light`` glyphs.

.. pack-preview:: fluent-regular

Using it
--------

.. pack-install:: fluent-regular

There is only one style, so this pack takes no ``style`` argument at all:

.. code-block:: python

   from tkinter_icons import FluentRegularIcon

   save = FluentRegularIcon("save-24", size=24)
   home = FluentRegularIcon("home-24", size=24)

Upstream's full spelling — ``ic-fluent-save-24-regular`` — resolves too, prefix, ``-regular`` suffix and all; this pack does not rewrite the names it was given. Everything :doc:`fluent` says about matching the ``-<size>-`` segment to the size you render at applies here unchanged.

Pack details
------------

.. pack-facts:: fluent-regular
