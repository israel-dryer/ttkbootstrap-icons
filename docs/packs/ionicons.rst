Ion Icons
=========

The Ionic Framework's set, drawn for touch. The glyphs are a little larger and a little heavier than a desktop set would be, because they were designed to be tapped rather than clicked, and that makes them read well in a toolbar at 24px and up.

This pack carries Ionicons 2, which is the last release built as an icon font — later versions ship as SVG only, so what you get here is the complete font-era set rather than a subset of a current one. Its vocabulary shows its age in places: there are ``android-`` and ``ios-`` prefixed variants of many icons, from an era when applications were expected to look different on each.

.. pack-preview:: ionicons

Using it
--------

.. pack-install:: ionicons

There are no styles, so the variant is part of the name:

.. code-block:: python

   from tkinter_icons import IonIcon

   home = IonIcon("home", size=24)
   home_outline = IonIcon("home-outline", size=24)
   settings = IonIcon("settings", size=24)

Names
-----

Three families share the namespace, and the browser is the fastest way to see which one has the icon you want:

.. code-block:: python

   IonIcon("cog-outline")            # the plain set
   IonIcon("android-settings")       # the Material-styled variants
   IonIcon("ion-ios-settings")       # the iOS-styled variants

Pack details
------------

.. pack-facts:: ionicons
