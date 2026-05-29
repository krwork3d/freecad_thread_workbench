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

"""Task panel for thread creation (logic + orchestration).  UI assembly in thread_ui.py."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets, QtCore

from translations import translate
from thread_presets import (
    inch_presets,
    suggest_metric_preset,
    find_inch_preset, suggest_inch_preset,
    profile_id_for_type,
)
from thread_builder import FaceAnalysis, create_thread
from thread_preview import ThreadPreview
import thread_ui


class ThreadTaskPanel:
    """Task panel: select a face, set parameters, and build a thread.

    Non-blocking — the user can freely switch selection.

    Parameters
    ----------
    thread_mode : "metric" | "inch"
    """

    def __init__(self, thread_mode="metric"):
        self._thread_mode = thread_mode
        # Resolve profile_id from the thread mode
        self._profile_id = profile_id_for_type(thread_mode)

        self._updating_ui = False
        self._analysis = FaceAnalysis()
        self._first_scan = True
        self._last_selection_key = None
        self._widgets = {}  # filled by _setup_ui
        self._preview = ThreadPreview()

        self._setup_ui()
        self.scan_selection()

        # Timer to poll selection changes
        self._poll_timer = QtCore.QTimer()
        self._poll_timer.setInterval(400)
        self._poll_timer.timeout.connect(self._poll_selection)
        self._poll_timer.start()

    # ═════════════════════════════════════════════════════════════
    # Task Panel protocol
    # ═════════════════════════════════════════════════════════════

    def getStandardButtons(self):
        return int(QtWidgets.QDialogButtonBox.StandardButton.Close.value)

    def clicked(self, bt):
        if bt == QtWidgets.QDialogButtonBox.Close:
            self.finish()

    def accept(self):
        self.finish()

    def reject(self):
        self.finish()

    def finish(self):
        self._poll_timer.stop()
        self._preview.remove()
        Gui.Control.closeDialog()

    # ═════════════════════════════════════════════════════════════
    # UI
    # ═════════════════════════════════════════════════════════════

    def _setup_ui(self):
        self.form, self._widgets = thread_ui.setup_ui(
            thread_mode=self._thread_mode,
            on_preset=self._on_preset,
            on_custom=self._on_custom,
            on_edge_to_edge=self._on_edge_to_edge,
            on_create=self._run,
            on_pitch_mm_changed=self._update_pitch_mm_label,
        )

        # ── Connect live preview signals ──
        w = self._widgets

        w["chk_preview"].toggled.connect(self._on_preview_toggled)

        # Connect ALL parameter changes to preview update
        if self._thread_mode == "metric":
            w["cb_diameter"].currentIndexChanged.connect(self._schedule_preview)
            w["spin_dia"].valueChanged.connect(self._schedule_preview)
            w["cb_pitch"].currentTextChanged.connect(self._schedule_preview)
            w["spin_pitch"].valueChanged.connect(self._schedule_preview)
        else:
            w["spin_dia"].valueChanged.connect(self._schedule_preview)
            w["spin_tpi"].valueChanged.connect(self._schedule_preview)

        w["spin_len"].valueChanged.connect(self._schedule_preview)
        w["spin_off"].valueChanged.connect(self._schedule_preview)
        w["cb_type"].currentIndexChanged.connect(self._schedule_preview)
        w["chk_reversed"].toggled.connect(self._schedule_preview)
        w["chk_left"].toggled.connect(self._schedule_preview)
        w["chk_e2e"].toggled.connect(self._schedule_preview)
        w["chk_runout"].toggled.connect(self._schedule_preview)
        w["cb_start_edge"].currentIndexChanged.connect(self._schedule_preview)

        # Debounce timer — avoids flicker during fast spinner changes
        self._preview_timer = QtCore.QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(200)  # 200 ms debounce
        self._preview_timer.timeout.connect(self._do_preview)

    def _schedule_preview(self):
        """Schedule a preview update (debounced)."""
        if self._widgets["chk_preview"].isChecked() and self._analysis.ok:
            self._preview_timer.start()

    # ── Presets ───────────────────────────────────────────────────

    def _on_preset(self, text):
        """Inch only — flat preset combo."""
        if self._updating_ui:
            return
        if text == translate("Custom", "— Custom —"):
            return
        w = self._widgets
        presets = inch_presets()
        dia_in, tpi = presets[text]
        self._updating_ui = True
        w["spin_dia"].setValue(dia_in)
        w["spin_tpi"].setValue(tpi)
        self._updating_ui = False
        self._update_pitch_mm_label()

    def _on_custom(self, _val=None):
        """Called when inch parameters are changed manually."""
        if self._updating_ui:
            return
        w = self._widgets
        self._updating_ui = True
        if self._thread_mode == "inch":
            preset = find_inch_preset(
                w["spin_dia"].value(), w["spin_tpi"].value()
            )
            idx = w["cb_preset"].findText(preset) if preset else 0
            w["cb_preset"].setCurrentIndex(idx if idx >= 0 else 0)
        self._updating_ui = False

    @property
    def _diameter_mm(self):
        """Return nominal diameter in mm."""
        w = self._widgets
        if self._thread_mode == "inch":
            return w["spin_dia"].value() * 25.4
        else:
            return w["spin_dia"].value()

    @property
    def _pitch_mm(self):
        """Return pitch in mm for create_thread."""
        w = self._widgets
        if self._thread_mode == "inch":
            return 25.4 / max(w["spin_tpi"].value(), 1)
        else:
            return w["spin_pitch"].value()

    def _update_pitch_mm_label(self):
        """Sync the pitch-in-mm label with TPI (inch mode)."""
        if self._thread_mode == "inch":
            pmm = 25.4 / max(self._widgets["spin_tpi"].value(), 1)
            self._widgets["lbl_pitch_mm"].setText(f"{pmm:.3f}")

    def _on_edge_to_edge(self, checked):
        """Enable/disable length fields based on auto-length mode."""
        self._widgets["spin_len"].setEnabled(not checked)
        self._widgets["spin_off"].setEnabled(not checked)

    # ── Live Preview ──────────────────────────────────────────────

    def _on_preview_toggled(self, checked):
        """Handle live preview checkbox toggle."""
        if checked:
            self._do_preview()
        else:
            self._preview.remove()

    def _do_preview(self):
        """Update the Coin3D preview overlay with current parameters."""
        if not self._analysis.ok:
            return

        w = self._widgets
        analysis = self._analysis

        edges = analysis.edges
        if not edges:
            return

        chosen_idx = w["cb_start_edge"].currentData()
        if chosen_idx is None:
            return

        chosen = next((e for e in edges if e[1] == chosen_idx), None)
        if chosen is None:
            return

        other = next((e for e in edges if e[1] != chosen_idx), None)
        preview_edges = [chosen] if other is None else [chosen, other]

        original_edges = analysis.edges
        analysis.edges = preview_edges

        try:
            self._preview.update(
                analysis,
                diameter=self._diameter_mm,
                pitch=self._pitch_mm,
                length=0.0 if w["chk_e2e"].isChecked()
                       else w["spin_len"].value(),
                offset=w["spin_off"].value(),
                is_external=(w["cb_type"].currentIndex() == 0),
                is_reversed=w["chk_reversed"].isChecked(),
                left_handed=w["chk_left"].isChecked(),
                profile_id=self._profile_id,
            )
        finally:
            analysis.edges = original_edges

    # ═════════════════════════════════════════════════════════════
    # Face scanning
    # ═════════════════════════════════════════════════════════════

    def scan_selection(self, force_suggest=False):
        # Remove preview from the previous face
        self._preview.remove()

        self._analysis = FaceAnalysis.from_selection()
        self._update_edge_combo()
        a = self._analysis
        w = self._widgets

        if not a.ok:
            w["lbl_status"].setText(f"⚠ {a.error}")
            return

        radius = a.radius

        if self._first_scan or force_suggest:
            self._updating_ui = True
            if self._thread_mode == "inch":
                preset_name, dia_in, tpi = suggest_inch_preset(radius)
                w["spin_dia"].setValue(dia_in)
                w["spin_tpi"].setValue(tpi)
                idx = w["cb_preset"].findText(preset_name)
                w["cb_preset"].setCurrentIndex(idx if idx >= 0 else 0)
                self._update_pitch_mm_label()
            else:
                dia, pitch = suggest_metric_preset(radius)
                w["spin_dia"].setValue(dia)
                w["spin_pitch"].setValue(pitch)
            self._updating_ui = False
            self._first_scan = False

        edges = a.edges
        if len(edges) >= 2:
            t0, idx0 = edges[0][0], edges[0][1]
            t1, idx1 = edges[-1][0], edges[-1][1]
            face_len = abs(t1 - t0)
            w["lbl_status"].setText(
                translate("status_two_edges",
                          "✓ Face: R={radius:.2f} mm, "
                          "face length ≈{face_len:.1f} mm. "
                          "Edges: #{idx0} and #{idx1}. Choose start edge.")
                .format(radius=radius, face_len=face_len,
                        idx0=idx0, idx1=idx1))
        elif len(edges) == 1:
            idx0 = edges[0][1]
            w["lbl_status"].setText(
                translate("status_one_edge",
                          "✓ Face: R={radius:.2f} mm. "
                          "Found 1 edge #{idx0}. Choose start edge.")
                .format(radius=radius, idx0=idx0))
        else:
            w["lbl_status"].setText(
                translate("status_no_edges",
                          "✓ Face: R={radius:.2f} mm. No circular edges found.")
                .format(radius=radius))

        # If preview is enabled, show it for the new face
        if w["chk_preview"].isChecked():
            self._do_preview()

    def _update_edge_combo(self):
        self._updating_ui = True
        cb = self._widgets["cb_start_edge"]
        cb.clear()
        edges = self._analysis.edges
        if not edges:
            cb.addItem(translate("no_edges", "— no edges —"))
            cb.setEnabled(False)
        else:
            cb.setEnabled(True)
            for t, idx, _ in edges:
                cb.addItem(f"Edge #{idx}  (t={t:.2f})", idx)
        self._updating_ui = False

    # ═════════════════════════════════════════════════════════════
    # Thread creation
    # ═════════════════════════════════════════════════════════════

    def _run(self):
        doc = App.ActiveDocument
        if not doc:
            QtWidgets.QMessageBox.warning(
                self.form,
                translate("ErrorTitle", "Error"),
                translate("err_no_document", "No active document!"))
            return

        # Remove preview and uncheck the box before creating the real thread
        self._preview.remove()
        self._widgets["chk_preview"].setChecked(False)

        self.scan_selection()
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
                runout=w["chk_runout"].isChecked(),
                profile_id=self._profile_id,
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

    # ═════════════════════════════════════════════════════════════
    # Auto-tracking selection changes
    # ═════════════════════════════════════════════════════════════

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
