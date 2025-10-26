"""
PyInstaller hook for ttkbootstrap_icons.

This hook ensures that the icon font files and metadata are included
when building frozen applications with PyInstaller.
"""

from PyInstaller.utils.hooks import collect_data_files

# Collect all data files from the assets directory
datas = collect_data_files('ttkbootstrap_icons.assets')