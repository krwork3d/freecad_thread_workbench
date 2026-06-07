# -*- coding: utf-8 -*-


"""Selection tracking mixin for ThreadTaskPanel."""

import FreeCADGui as Gui


class SelectionMixin:
    """Provides automatic selection change detection."""

    def _poll_selection(self):
        """Periodically check whether the selected face has changed."""
        try:
            sel = Gui.Selection.getSelectionEx()
        except Exception:
            return

        if not sel:
            key = None
        else:
            key = (sel[0].Object, sel[0].SubElementNames[0]
                   if sel[0].SubElementNames else None)

        if key == self._last_selection_key:
            return

        self._last_selection_key = key
        self._first_scan = True
        self.scan_selection()
