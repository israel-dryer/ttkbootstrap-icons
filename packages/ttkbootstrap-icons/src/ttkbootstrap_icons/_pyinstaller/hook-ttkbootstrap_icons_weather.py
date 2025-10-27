"""PyInstaller hook to include provider data files for ttkbootstrap_icons_weather."""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('ttkbootstrap_icons_weather')

