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

"""Thread creation mixin for ThreadTaskPanel."""

import FreeCAD as App
from PySide import QtWidgets

from freecad.ThreadWorkbench.translations import translate
from freecad.ThreadWorkbench.geometry import create_thread


class CreationMixin:
    """Provides thread creation functionality."""

    def _run(self):
        """Create the thread feature in the active document."""
        doc = App.ActiveDocument
        if not doc:
            QtWidgets.QMessageBox.warning(
                self.form,
                translate("ErrorTitle", "Error"),
                translate("err_no_document", "No active document!"))
            return

        # Save the user's edge choice BEFORE scan_selection() clears the
        # combo box (it calls _update_edge_combo which resets index to 0).
        w = self._widgets
        saved_edge_idx = w["cb_start_edge"].currentData()

        # Remove preview and uncheck the box before creating the real thread
        self._preview.remove()
        self._widgets["chk_preview"].setChecked(False)

        self.scan_selection()

        # Restore the user's edge choice after scan_selection rebuilt the
        # combo. If the saved index is no longer in the list (edge of a
        # different face), the combo will stay at its default (index 0).
        cb = w["cb_start_edge"]
        if saved_edge_idx is not None and cb.count() > 0:
            for i in range(cb.count()):
                if cb.itemData(i) == saved_edge_idx:
                    cb.setCurrentIndex(i)
                    break

        if not self._analysis.ok:
            QtWidgets.QMessageBox.warning(
                self.form,
                translate("ErrorTitle", "Error"),
                self._analysis.error)
            return

        edges = self._analysis.edges
        if not edges:
            QtWidgets.QMessageBox.warning(
                self.form,
                translate("ErrorTitle", "Error"),
                translate("err_no_circular_edges",
                          "No circular edges found on the selected face!"))
            return

        w = self._widgets
        chosen_idx = w["cb_start_edge"].currentData()
        if chosen_idx is None:
            QtWidgets.QMessageBox.warning(
                self.form,
                translate("ErrorTitle", "Error"),
                translate("err_no_start_edge",
                          "Choose a start edge!"))
            return

        chosen = next((e for e in edges if e[1] == chosen_idx), None)
        other = next((e for e in edges if e[1] != chosen_idx), None)
        if chosen is None:
            QtWidgets.QMessageBox.warning(
                self.form,
                translate("ErrorTitle", "Error"),
                translate("err_edge_not_found",
                          "Chosen edge not found!"))
            return

        analysis = self._analysis
        analysis.edges = [chosen] if other is None else [chosen, other]

        doc.openTransaction(translate("TransactionName", "Create Thread"))
        try:
            create_thread(
                analysis,
                diameter=self._diameter_mm,
                pitch=self._pitch_mm,
                length=0.0 if w["chk_e2e"].isChecked()
                       else w["spin_len"].value(),
                offset=w["spin_off"].value(),
                is_external=(w["cb_type"].currentIndex() == 0),
                is_reversed=w["chk_reversed"].isChecked(),
                left_handed=w["chk_left"].isChecked(),
                runout=w["cb_runout"].currentData(),
                profile_id=self._profile_id,
                clearance=w["spin_clearance"].value(),
            )
            doc.commitTransaction()
        except RuntimeError as e:
            doc.abortTransaction()
            QtWidgets.QMessageBox.critical(
                self.form,
                translate("ErrorTitle", "Error"),
                str(e))
            return

        w["lbl_status"].setText(
            translate("done", "✓ Thread created! You can select another face."))
