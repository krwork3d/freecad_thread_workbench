# -*- coding: utf-8 -*-

"""Preview mixin for ThreadTaskPanel."""


class PreviewMixin:
    """Provides live preview functionality."""

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

    def _schedule_preview(self):
        """Schedule a preview update (debounced)."""
        if self._widgets["chk_preview"].isChecked() and self._analysis.ok:
            self._preview_timer.start()

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
                clearance=w["spin_clearance"].value(),
            )
        finally:
            analysis.edges = original_edges
