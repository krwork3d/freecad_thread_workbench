# -*- coding: utf-8 -*-
# Thread Workbench — init_gui.py
# Registers the workbench with FreeCAD's GUI.
#
# When loaded via <subdirectory> in package.xml, FreeCAD imports this
# module — __file__ is available and points inside the addon.

import os

import FreeCADGui as Gui

from freecad.ThreadWorkbench import ADDON_ROOT


class ThreadWorkbench(Gui.Workbench):
    """Generator of metric and inch threads for PartDesign::Body."""

    MenuText = "Thread"
    ToolTip = "Create metric (ISO 724) and inch (UNC/UNF) threads in PartDesign"

    def __init__(self):
        Gui.Workbench.__init__(self)

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        from freecad.ThreadWorkbench import thread_commands

        # Register translations — relative to addon root
        Gui.addLanguagePath(os.path.join(ADDON_ROOT, "translations"))
        Gui.updateLocale()

        self.appendToolbar(
            "Thread", ["ThreadCreate", "ThreadInchCreate"])
        self.appendMenu(
            "Thread", ["ThreadCreate", "ThreadInchCreate"])
        Gui.addCommand("ThreadCreate", thread_commands.ThreadCreateCommand())
        Gui.addCommand("ThreadInchCreate", thread_commands.ThreadInchCommand())

    def Activated(self):
        pass

    def Deactivated(self):
        pass


ThreadWorkbench.Icon = os.path.join(
    ADDON_ROOT, "Resources", "Icons", "ThreadWorkbench.svg")
ThreadWorkbench.commands = ["ThreadCreate", "ThreadInchCreate"]

Gui.addWorkbench(ThreadWorkbench())
