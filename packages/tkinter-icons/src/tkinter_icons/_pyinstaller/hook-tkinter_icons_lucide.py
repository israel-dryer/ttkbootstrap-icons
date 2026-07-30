"""PyInstaller hook to include provider data files for tkinter_icons_lucide."""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('tkinter_icons_lucide')

