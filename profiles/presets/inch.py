# -*- coding: utf-8 -*-
"""Inch thread preset table ASME B1.1 (UNC/UNF).

Structure of _raw_data:
    {
        "UNC": {name: (d_inch, tpi), ...},
        "UNF": {name: (d_inch, tpi), ...},
    }

Public API:
    - preset_names             -> list[str]
    - all_presets              -> {name: (d_inch, tpi), ...}
    - find_preset(d_inch, tpi) -> str|None
    - suggest_preset(r_mm)     -> (name, d_inch, tpi)
"""

from profiles.presets.base import AbstractPresetTable
from profiles.presets.registry import register_preset_table


# ═══════════════════════════════════════════════════════════════════
# Data: name -> (major_diameter_inch, TPI)
# ═══════════════════════════════════════════════════════════════════

_UNC = {
    "#1-64 UNC":    (0.073, 64),
    "#2-56 UNC":    (0.086, 56),
    "#3-48 UNC":    (0.099, 48),
    "#4-40 UNC":    (0.112, 40),
    "#5-40 UNC":    (0.125, 40),
    "#6-32 UNC":    (0.138, 32),
    "#8-32 UNC":    (0.164, 32),
    "#10-24 UNC":   (0.190, 24),
    "1/4-20 UNC":   (0.250, 20),
    "5/16-18 UNC":  (0.3125, 18),
    "3/8-16 UNC":   (0.375, 16),
    "7/16-14 UNC":  (0.4375, 14),
    "1/2-13 UNC":   (0.500, 13),
    "9/16-12 UNC":  (0.5625, 12),
    "5/8-11 UNC":   (0.625, 11),
    "3/4-10 UNC":   (0.750, 10),
    "7/8-9 UNC":    (0.875, 9),
    "1-8 UNC":      (1.000, 8),
    "1 1/8-7 UNC":  (1.125, 7),
    "1 1/4-7 UNC":  (1.250, 7),
    "1 3/8-6 UNC":  (1.375, 6),
    "1 1/2-6 UNC":  (1.500, 6),
    "1 3/4-5 UNC":  (1.750, 5),
    "2-4.5 UNC":    (2.000, 4.5),
}

_UNF = {
    "#0-80 UNF":    (0.060, 80),
    "#1-72 UNF":    (0.073, 72),
    "#2-64 UNF":    (0.086, 64),
    "#3-56 UNF":    (0.099, 56),
    "#4-48 UNF":    (0.112, 48),
    "#5-44 UNF":    (0.125, 44),
    "#6-40 UNF":    (0.138, 40),
    "#8-36 UNF":    (0.164, 36),
    "#10-32 UNF":   (0.190, 32),
    "1/4-28 UNF":   (0.250, 28),
    "5/16-24 UNF":  (0.3125, 24),
    "3/8-24 UNF":   (0.375, 24),
    "7/16-20 UNF":  (0.4375, 20),
    "1/2-20 UNF":   (0.500, 20),
    "9/16-18 UNF":  (0.5625, 18),
    "5/8-18 UNF":   (0.625, 18),
    "3/4-16 UNF":   (0.750, 16),
    "7/8-14 UNF":   (0.875, 14),
    "1-12 UNF":     (1.000, 12),
}


@register_preset_table
class InchPresetTable(AbstractPresetTable):
    """Inch thread preset table ASME B1.1 (UNC/UNF)."""

    profile_id = "asme_b11"
    table_type = "inch"
    label = "ASME B1.1 (UNC/UNF)"

    # ── Data building ──────────────────────────────────────────

    def _build_raw_data(self):
        return {
            "UNC": dict(_UNC),
            "UNF": dict(_UNF),
        }

    # ── Preset names ─────────────────────────────────────────────

    @property
    def preset_names(self):
        """list[str] — all preset names (UNC + UNF)."""
        result = []
        for name in self._raw_data["UNC"]:
            result.append(name)
        for name in self._raw_data["UNF"]:
            result.append(name)
        return result

    # ── All presets as a flat list ────────────────────────────────

    @property
    def all_presets(self):
        """dict[name] -> (d_inch, tpi) — all presets."""
        result = {}
        result.update(self._raw_data["UNC"])
        result.update(self._raw_data["UNF"])
        return result

    # ── Search ──────────────────────────────────────────────────────

    def find_preset(self, diameter_inch, tpi):
        """Find a preset name by diameter (inches) and TPI.

        Returns str (name) or None.
        """
        for name, (d, t) in self.all_presets.items():
            if abs(d - diameter_inch) < 0.0005 and t == tpi:
                return name
        return None

    # ── Suggestion ─────────────────────────────────────────────────────

    def suggest_preset(self, radius_mm):
        """Suggest the nearest inch preset by face radius (mm).

        Returns (preset_name, diameter_inch, tpi).
        """
        from translations import translate

        detected_inch = radius_mm * 2.0 / 25.4
        sorted_presets = sorted(
            self.all_presets.items(), key=lambda x: x[1][0]
        )
        for name, (d, t) in sorted_presets:
            if d >= detected_inch - 0.0005:
                return (name, d, t)
        return (translate("Custom", "— Custom —"), detected_inch, 20)