Getting started
===============

Four short pages: install a pack, draw an icon, work out which set you want, and — if you are arriving from ``ttkbootstrap-icons`` — move your existing code over.

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Installation
      :link: installation
      :link-type: doc

      Installing a pack as an extra, what the quotes are for, and what the base package does not give you.

   .. grid-item-card:: Quickstart
      :link: quickstart
      :link-type: doc

      An icon on a button in ten lines, and the three things about it that matter later.

   .. grid-item-card:: Choosing a pack
      :link: choosing-a-pack
      :link-type: doc

      Sixteen sets, and how to pick without reading all of them.

   .. grid-item-card:: Migrating
      :link: migrating
      :link-type: doc

      Coming from ``ttkbootstrap-icons`` 4.0.0. Your code keeps working; two things genuinely changed.

In short
--------

.. code-block:: bash

   pip install "tkinter-icons[material]"

.. code-block:: python

   from tkinter_icons import MaterialIcon

   home = MaterialIcon("home", size=24, color="#0d6efd")
   ttk.Button(root, text="Home", image=home.image, compound="left").pack()

.. toctree::
   :hidden:

   installation
   quickstart
   choosing-a-pack
   migrating
