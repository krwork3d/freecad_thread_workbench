# -*- coding: utf-8 -*-

"""Preset handling mixin for ThreadTaskPanel."""

from freecad.ThreadWorkbench.translations import translate
from freecad.ThreadWorkbench.thread_presets import (
    inch_presets, find_inch_preset,
    bsp_presets, find_bsp_preset,
)


class PresetsMixin:
    """Provides preset selection and custom parameter handling."""

    @property
    def _is_tpi_mode(self):
        """True for TPI-based thread modes (inch, bsp)."""
        return self._thread_mode in ("inch", "bsp")

    def _presets_dict(self):
        """Return the preset dict for the current thread mode."""
        if self._thread_mode == "bsp":
            return bsp_presets()
        return inch_presets()

    def _find_preset(self, dia_in, tpi):
        """Find a preset name for the current thread mode."""
        if self._thread_mode == "bsp":
            return find_bsp_preset(dia_in, tpi)
        return find_inch_preset(dia_in, tpi)

    def _on_preset(self, text):
        """TPI modes (inch / bsp) — flat preset combo."""
        if self._updating_ui:
            return
        if text == translate("Custom", "— Custom —"):
            return
        w = self._widgets
        presets = self._presets_dict()
        dia_in, tpi = presets[text]
        self._updating_ui = True
        w["spin_dia"].setValue(dia_in)
        w["spin_tpi"].setValue(tpi)
        self._updating_ui = False
        self._update_pitch_mm_label()

    def _on_custom(self, _val=None):
        """Called when TPI parameters are changed manually."""
        if self._updating_ui:
            return
        w = self._widgets
        self._updating_ui = True
        if self._is_tpi_mode:
            preset = self._find_preset(
                w["spin_dia"].value(), w["spin_tpi"].value()
            )
            idx = w["cb_preset"].findText(preset) if preset else 0
            w["cb_preset"].setCurrentIndex(idx if idx >= 0 else 0)
        self._updating_ui = False

    def _update_pitch_mm_label(self):
        """Sync the pitch-in-mm label with TPI (inch / bsp mode)."""
        if self._is_tpi_mode:
            pmm = 25.4 / max(self._widgets["spin_tpi"].value(), 1)
            self._widgets["lbl_pitch_mm"].setText(f"{pmm:.3f}")

    def _on_edge_to_edge(self, checked):
        """Enable/disable length fields based on auto-length mode."""
        self._widgets["spin_len"].setEnabled(not checked)
        # Offset remains editable in edge-to-edge mode
        self._widgets["spin_off"].setEnabled(True)
