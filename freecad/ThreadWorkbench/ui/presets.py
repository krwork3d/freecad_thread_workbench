# -*- coding: utf-8 -*-

"""Preset handling mixin for ThreadTaskPanel."""

from freecad.ThreadWorkbench.translations import translate
from freecad.ThreadWorkbench.thread_presets import inch_presets, find_inch_preset


class PresetsMixin:
    """Provides preset selection and custom parameter handling."""

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

    def _update_pitch_mm_label(self):
        """Sync the pitch-in-mm label with TPI (inch mode)."""
        if self._thread_mode == "inch":
            pmm = 25.4 / max(self._widgets["spin_tpi"].value(), 1)
            self._widgets["lbl_pitch_mm"].setText(f"{pmm:.3f}")

    def _on_edge_to_edge(self, checked):
        """Enable/disable length fields based on auto-length mode."""
        self._widgets["spin_len"].setEnabled(not checked)
        self._widgets["spin_off"].setEnabled(not checked)
