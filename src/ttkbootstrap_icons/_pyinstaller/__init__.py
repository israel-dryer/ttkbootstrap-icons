"""PyInstaller hooks for ttkbootstrap_icons."""

import os


def get_hook_dirs():
    """Return the directory containing PyInstaller hooks for this package."""
    return [os.path.dirname(__file__)]