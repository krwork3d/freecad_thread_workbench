# -*- coding: utf-8 -*-
# Thread Workbench — freecad.ThreadWorkbench namespace initializer.
# FreeCAD loads this module at startup in any mode.
import os

__version__ = "0.2.0"

# Absolute path to the addon root directory.
# This module lives at: <addon_root>/freecad/ThreadWorkbench/__init__.py
# So addon root is 3 levels up (.. / .. / ..).
ADDON_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
