# -*- coding: utf-8 -*-
# Thread Workbench - InitGui.py
# FreeCAD exec()s this file, so __file__ is not set.

import os
import sys

import FreeCAD as App
import FreeCADGui as Gui


class ThreadWorkbench(Gui.Workbench):
    """Generator of metric and inch threads for PartDesign::Body."""

    MenuText = "Thread"
    ToolTip = "Create metric (ISO 724) and inch (UNC/UNF) threads in PartDesign"

    def __init__(self):
        Gui.Workbench.__init__(self)

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        import thread_commands

        # Register translations — standard FreeCAD way
        trans_dir = os.path.join(
            App.getUserAppDataDir(), "Mod", "ThreadWorkbench", "translations")
        Gui.addLanguagePath(trans_dir)
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


wb_dir = os.path.join(App.getUserAppDataDir(), "Mod", "ThreadWorkbench")
if wb_dir not in sys.path:
    sys.path.insert(0, wb_dir)

ThreadWorkbench.Icon = os.path.join(wb_dir, "icons", "ThreadWorkbench.svg")
ThreadWorkbench.commands = ["ThreadCreate", "ThreadInchCreate"]

Gui.addWorkbench(ThreadWorkbench())
