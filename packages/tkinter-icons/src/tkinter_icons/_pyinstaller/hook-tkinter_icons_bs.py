"""PyInstaller hook to include provider data files for tkinter_icons_bs.

Unlike the other packs, this one keeps its font and JSON in an `assets`
subpackage rather than at the module root. `collect_data_files` walks
subpackages, so naming the top-level package still reaches them.
"""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('tkinter_icons_bs')