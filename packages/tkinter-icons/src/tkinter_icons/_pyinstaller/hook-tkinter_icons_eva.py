"""PyInstaller hook to include provider data files for tkinter_icons_eva."""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('tkinter_icons_eva')

