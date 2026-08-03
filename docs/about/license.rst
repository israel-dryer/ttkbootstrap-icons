License
=======

The library
-----------

``tkinter-icons`` and all sixteen packs are MIT licensed. That covers the code in this repository: the renderer, the browser, the provider classes, and each pack's Python.

.. code-block:: text

   MIT License

   Copyright (c) 2026 Israel Dryer

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
   THE SOFTWARE.

The icons
---------

**The icons are not ours, and MIT is not their license.** Each pack redistributes an upstream icon font under that project's own terms, and ships the license text inside the installed package under ``LICENSES/``.

Most are permissive — MIT, Apache 2.0, ISC, SIL OFL, CC0 — and drawing the glyphs in your application is exactly what they are for. A few carry conditions worth knowing about:

* **Attribution.** Font Awesome's icons (CC BY 4.0), Weather Icons' documentation (CC BY 3.0), and Typicons' artwork (CC BY-SA 4.0) ask to be credited. Shipping the pack carries the license text; an application with an about or credits screen should name the icon set there.
* **Share-alike.** Typicons' artwork is CC BY-SA 4.0. That binds *adaptations of the artwork* — redrawing the icons — not an application that draws them.
* **Fonts under the SIL OFL** may be bundled and redistributed freely, but not sold on their own.

`THIRD-PARTY-NOTICES.md <https://github.com/israel-dryer/tkinter-icons/blob/main/THIRD-PARTY-NOTICES.md>`_ lists every pack with its upstream source, license, and the files it ships. :doc:`../packs` links each pack's upstream license directly, and the icon browser shows a License link for whichever set you are looking at.

.. note::

   This page is a summary written to help you find the right document, not legal advice. Where it and an upstream license disagree, the upstream license is the one that counts.