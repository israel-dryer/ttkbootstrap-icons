Simple Icons
============

Brand and product marks — thousands of them, and very close to exhaustive for anything with a logo and a public presence. If a company, language, service, or tool has a mark, this pack probably has it.

It is not a user interface set and does not pretend to be: there is no "save", no "settings", no arrow. Where :doc:`devicon` is narrower and aimed at developer tooling — often with a wordmark variant — Simple Icons is broader and gives you the mark alone.

.. pack-preview:: simple

Using it
--------

.. pack-install:: simple

.. code-block:: python

   from tkinter_icons import SimpleIcon

   github = SimpleIcon("github", size=20)
   docker = SimpleIcon("docker", size=20)
   python = SimpleIcon("python", size=20, color="#3776AB")

Pairing it with a UI set
------------------------

Because there is no "save" icon here, an application that needs one draws from two packs. That costs a second extra and nothing else — each icon holds its own icon set, so the two never interfere.

.. code-block:: bash

   pip install "tkinter-icons[lucide,simple]"

.. code-block:: python

   from tkinter_icons import LucideIcon, SimpleIcon

   save = LucideIcon("save", size=20)
   github = SimpleIcon("github", size=20)

Any general-purpose pack works in place of :doc:`lucide`; see :doc:`../packs` for the sixteen.

Names
-----

Names are the brand, lowercased, with spaces removed and punctuation spelled out — a dot becomes ``dot``, a plus becomes ``plus``:

.. code-block:: python

   SimpleIcon("githubactions")
   SimpleIcon("nodedotjs")       # Node.js
   SimpleIcon("cplusplus")       # C++

.. note::

   These are trademarks. The pack's license covers the drawings, not the right to use a company's mark — check with the brand before putting one in a product. ``THIRD-PARTY-NOTICES.md`` in the repository has the details.

Pack details
------------

.. pack-facts:: simple
