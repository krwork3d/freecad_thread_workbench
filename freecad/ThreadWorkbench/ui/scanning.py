# -*- coding: utf-8 -*-


"""Face scanning mixin for ThreadTaskPanel."""

from freecad.ThreadWorkbench.translations import translate
from freecad.ThreadWorkbench.geometry import FaceAnalysis
from freecad.ThreadWorkbench.thread_presets import (
    suggest_metric_preset, suggest_inch_preset, suggest_bsp_preset,
)


class ScanningMixin:
    """Provides face scanning and edge detection functionality."""

    def scan_selection(self, force_suggest=False):
        """Scan the currently selected face and update UI accordingly."""
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
            if self._thread_mode in ("inch", "bsp"):
                if self._thread_mode == "bsp":
                    preset_name, dia_in, tpi = suggest_bsp_preset(radius)
                else:
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
        """Update the start edge combo box based on current analysis."""
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

