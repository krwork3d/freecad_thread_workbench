# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Thread Workbench for FreeCAD                                          *
# *   Copyright (c) 2025                                                    *
# *                                                                         *
# *   This program is free software: you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation, either version 3 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU General Public License for more details.                          *
# *                                                                         *
# *   You should have received a copy of the GNU General Public License     *
# *   along with this program.  If not, see <http://www.gnu.org/licenses/>. *
# ***************************************************************************

"""Thread creation commands for the Thread Workbench."""

import os
import FreeCAD as App
import FreeCADGui as Gui

from freecad.ThreadWorkbench import ADDON_ROOT


def QT_TRANSLATE_NOOP(context, text):
    """no-op marker for lupdate — returns text unchanged at runtime."""
    return text

ICONDIR = os.path.join(ADDON_ROOT, "Resources", "Icons")


class ThreadCreateCommand:
    """Command: open the thread generation dialog."""

    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONDIR, "ThreadCreate.svg"),
            "MenuText": QT_TRANSLATE_NOOP("ThreadCreate",
                                           "Create thread"),
            "ToolTip": QT_TRANSLATE_NOOP("ThreadCreate",
                                          "Create a metric thread on a cylindrical "
                                          "face inside a PartDesign::Body"),
        }

    def IsActive(self):
        return (
            App.ActiveDocument is not None
            and Gui.Selection.hasSelection()
        )

    def Activated(self):
        from freecad.ThreadWorkbench.thread_dialog import ThreadTaskPanel
        panel = ThreadTaskPanel(thread_mode="metric")
        Gui.Control.showDialog(panel)


class ThreadInchCommand:
    """Command: open the inch thread generation dialog."""

    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICONDIR, "ThreadInchCreate.svg"),
            "MenuText": QT_TRANSLATE_NOOP("ThreadInchCreate",
                                           "Create inch thread"),
            "ToolTip": QT_TRANSLATE_NOOP("ThreadInchCreate",
                                          "Create an inch thread (UNC/UNF) on a "
                                          "cylindrical face inside a PartDesign::Body"),
        }

    def IsActive(self):
        return (
            App.ActiveDocument is not None
            and Gui.Selection.hasSelection()
        )

    def Activated(self):
        from freecad.ThreadWorkbench.thread_dialog import ThreadTaskPanel
        panel = ThreadTaskPanel(thread_mode="inch")
        Gui.Control.showDialog(panel)
