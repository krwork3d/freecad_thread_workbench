# -*- coding: utf-8 -*-
"""Metric thread preset table ISO 724 (ISO 68-1 profile).

All preset data lives in ``presets.json`` next to this module, organised
the same way the UI consumes it: each size lists the pitches available
for that diameter (coarse first, fine descending).  This file only
contains the type-specific search/suggestion logic — adding or editing
presets is a JSON-only change.

JSON schema for one size entry::

    {"diameter_mm": 10.0, "pitches_mm": [1.5, 1.25, 1.0, 0.75]}

The first (largest) pitch is treated as *coarse* and shown as ``M10``;
subsequent pitches are *fine* and shown as ``M10×1.25`` etc.

Public API (used by the UI):
    - preset_names          -> list[str]
    - diameters             -> list[float]
    - pitches_for(d_mm)     -> list[(p_mm, name)]
    - find_preset(d, p)     -> str | None
    - suggest_preset(r_mm)  -> (d_mm, p_mm)
"""

from threads.base import AbstractPresetTable
from threads.registry import register_preset_table


# Floating-point tolerance for diameter / pitch comparisons (in mm).
_EPS = 1e-3


@register_preset_table
class MetricPresetTable(AbstractPresetTable):
    """Metric thread preset table ISO 724 — data-driven from presets.json."""

    # Identity is read from the manifest; no need to duplicate here.

    # ── Name formatting ──────────────────────────────────────────────

    @staticmethod
    def _fmt(value):
        """Format a float with no trailing zeros: 10.0 → '10', 1.25 → '1.25'."""
        return f"{value:g}"

    @classmethod
    def _name_for(cls, diameter_mm, pitch_mm, is_coarse):
        """Build the preset name 'M10' (coarse) or 'M10×1.25' (fine)."""
        d_str = cls._fmt(diameter_mm)
        if is_coarse:
            return f"M{d_str}"
        return f"M{d_str}\u00d7{cls._fmt(pitch_mm)}"

    @staticmethod
    def _ordered_pitches(size):
        """Return pitches sorted descending (coarse first)."""
        return sorted(size["pitches_mm"], reverse=True)

    # ── Public accessors ─────────────────────────────────────────────

    @property
    def diameters(self):
        """list[float] — all diameters, sorted ascending."""
        return sorted({s["diameter_mm"] for s in self.sizes})

    @property
    def preset_names(self):
        """list[str] — every preset name in canonical order."""
        result = []
        for size in self.sizes:
            d = size["diameter_mm"]
            for i, p in enumerate(self._ordered_pitches(size)):
                result.append(self._name_for(d, p, is_coarse=(i == 0)))
        return result

    def pitches_for(self, diameter_mm):
        """list[(pitch_mm, name)] for the given diameter, coarse first."""
        for size in self.sizes:
            if abs(size["diameter_mm"] - diameter_mm) < _EPS:
                d = size["diameter_mm"]
                pitches = self._ordered_pitches(size)
                return [
                    (p, self._name_for(d, p, is_coarse=(i == 0)))
                    for i, p in enumerate(pitches)
                ]
        return []

    # ── Search ──────────────────────────────────────────────────────

    def find_preset(self, diameter_mm, pitch_mm):
        """Find a preset name by diameter and pitch.  Returns str or None."""
        for size in self.sizes:
            if abs(size["diameter_mm"] - diameter_mm) >= _EPS:
                continue
            d = size["diameter_mm"]
            for i, p in enumerate(self._ordered_pitches(size)):
                if abs(p - pitch_mm) < _EPS:
                    return self._name_for(d, p, is_coarse=(i == 0))
        return None

    # ── Suggestion ──────────────────────────────────────────────────

    def suggest_preset(self, radius_mm):
        """Suggest a diameter and coarse pitch by face radius (mm).

        If a standard preset matches the detected diameter exactly (within
        1 µm), return its coarse pitch.  Otherwise return the detected
        diameter as-is so the UI shows «— Custom —».

        Returns (diameter_mm, pitch_mm).
        """
        detected_diameter = radius_mm * 2.0
        for size in self.sizes:
            if abs(size["diameter_mm"] - detected_diameter) < _EPS:
                pitches = self._ordered_pitches(size)
                if pitches:
                    return (size["diameter_mm"], pitches[0])
                return (size["diameter_mm"], 1.5)
        # No exact match — let the UI fall back to Custom.
        return (detected_diameter, 1.5)
