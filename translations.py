# -*- coding: utf-8 -*-
"""Translation helpers for Thread Workbench.

Uses FreeCAD.Qt.translate — the standard for workbenches.
See https://wiki.freecad.org/Translating_an_external_workbench
"""

import FreeCAD as App

CONTEXT = "ThreadWorkbench"


def translate(source_text, disambiguation=None):
    """Translate *source_text* (English user-visible string) using FreeCAD's Qt.

    Returns the translated string for the current locale, or *source_text*
    unchanged if no `.qm` translation is installed.

    *disambiguation* is only needed when identical source_text appears in
    multiple places with different meanings (e.g. "External" for thread type
    vs. external reference).
    """
    try:
        if disambiguation:
            return App.Qt.translate(CONTEXT, source_text, disambiguation)
        return App.Qt.translate(CONTEXT, source_text)
    except AttributeError:
        return source_text
