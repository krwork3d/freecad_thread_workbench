# -*- coding: utf-8 -*-
"""Metric thread preset table ISO 724 (ISO 68-1 profile).

Structure of _raw_data:
    {
        "coarse": [(d_mm, p_mm, name), ...],
        "fine":   [(d_mm, p_mm, name), ...],
    }

Public API:
    - preset_names          -> list[str]  (all names, coarse + fine)
    - diameters             -> list[float] (unique diameters)
    - pitches_for(d_mm)     -> list[(p_mm, name)]  (pitches for a diameter)
    - find_preset(d, p)     -> str|None
    - suggest_preset(r_mm)  -> (d_mm, p_mm)
"""

from profiles.presets.base import AbstractPresetTable
from profiles.presets.registry import register_preset_table


# ═══════════════════════════════════════════════════════════════════
# Data: (diameter_mm, pitch_mm, preset_name)
# ═══════════════════════════════════════════════════════════════════

_COARSE = [
    (2.0,   0.4,   "M2"),
    (2.5,   0.45,  "M2.5"),
    (3.0,   0.5,   "M3"),
    (4.0,   0.7,   "M4"),
    (5.0,   0.8,   "M5"),
    (6.0,   1.0,   "M6"),
    (8.0,   1.25,  "M8"),
    (10.0,  1.5,   "M10"),
    (12.0,  1.75,  "M12"),
    (14.0,  2.0,   "M14"),
    (16.0,  2.0,   "M16"),
    (18.0,  2.5,   "M18"),
    (20.0,  2.5,   "M20"),
    (22.0,  2.5,   "M22"),
    (24.0,  3.0,   "M24"),
    (27.0,  3.0,   "M27"),
    (30.0,  3.5,   "M30"),
    (33.0,  3.5,   "M33"),
    (36.0,  4.0,   "M36"),
    (39.0,  4.0,   "M39"),
    (42.0,  4.5,   "M42"),
    (45.0,  4.5,   "M45"),
    (48.0,  5.0,   "M48"),
    (52.0,  5.0,   "M52"),
    (56.0,  5.5,   "M56"),
    (60.0,  5.5,   "M60"),
    (64.0,  6.0,   "M64"),
    (68.0,  6.0,   "M68"),
]

_FINE = [
    (8.0,   1.0,   "M8×1"),
    (10.0,  1.25,  "M10×1.25"),
    (10.0,  1.0,   "M10×1"),
    (10.0,  0.75,  "M10×0.75"),
    (12.0,  1.5,   "M12×1.5"),
    (12.0,  1.25,  "M12×1.25"),
    (12.0,  1.0,   "M12×1"),
    (14.0,  1.5,   "M14×1.5"),
    (16.0,  1.5,   "M16×1.5"),
    (18.0,  2.0,   "M18×2"),
    (18.0,  1.5,   "M18×1.5"),
    (20.0,  2.0,   "M20×2"),
    (20.0,  1.5,   "M20×1.5"),
    (22.0,  2.0,   "M22×2"),
    (22.0,  1.5,   "M22×1.5"),
    (24.0,  2.0,   "M24×2"),
    (27.0,  2.0,   "M27×2"),
    (30.0,  3.0,   "M30×3"),
    (30.0,  2.0,   "M30×2"),
    (33.0,  2.0,   "M33×2"),
    (36.0,  3.0,   "M36×3"),
    (39.0,  3.0,   "M39×3"),
    (42.0,  4.0,   "M42×4"),
    (42.0,  3.0,   "M42×3"),
    (45.0,  4.0,   "M45×4"),
    (45.0,  3.0,   "M45×3"),
    (48.0,  4.0,   "M48×4"),
    (48.0,  3.0,   "M48×3"),
    (52.0,  4.0,   "M52×4"),
    (52.0,  3.0,   "M52×3"),
    (56.0,  4.0,   "M56×4"),
    (60.0,  4.0,   "M60×4"),
    (64.0,  4.0,   "M64×4"),
    (68.0,  4.0,   "M68×4"),
]


@register_preset_table
class MetricPresetTable(AbstractPresetTable):
    """Metric thread preset table ISO 724."""

    profile_id = "iso68_1"
    table_type = "metric"
    label = "ISO 724 (Metric)"

    # ── Data building ──────────────────────────────────────────

    def _build_raw_data(self):
        return {
            "coarse": list(_COARSE),
            "fine": list(_FINE),
        }

    # ── Preset names ─────────────────────────────────────────────

    @property
    def preset_names(self):
        """list[str] — all preset names (coarse + fine)."""
        result = []
        for entry in self._raw_data["coarse"]:
            result.append(entry[2])
        for entry in self._raw_data["fine"]:
            result.append(entry[2])
        return result

    # ── Diameters and pitches ────────────────────────────────────────────

    @property
    def diameters(self):
        """list[float] — unique diameters, sorted."""
        seen = set()
        result = []
        for entry in self._raw_data["coarse"]:
            d = entry[0]
            if d not in seen:
                seen.add(d)
                result.append(d)
        for entry in self._raw_data["fine"]:
            d = entry[0]
            if d not in seen:
                seen.add(d)
                result.append(d)
        result.sort()
        return result

    def pitches_for(self, diameter_mm):
        """Return list[(pitch_mm, name)] for the given diameter.

        Pitches are sorted descending (coarse pitch first).
        """
        result = {}
        for entry in self._raw_data["coarse"]:
            d, p, n = entry
            if abs(d - diameter_mm) < 0.001:
                result[p] = n
        for entry in self._raw_data["fine"]:
            d, p, n = entry
            if abs(d - diameter_mm) < 0.001:
                result[p] = n
        # Sort by pitch descending
        sorted_pitches = sorted(result.items(), key=lambda x: -x[0])
        return [(p, n) for p, n in sorted_pitches]

    # ── Search ──────────────────────────────────────────────────────

    def find_preset(self, diameter_mm, pitch_mm):
        """Find a preset name by diameter and pitch.

        Returns str (name) or None.
        """
        for entry in self._raw_data["coarse"]:
            d, p, n = entry
            if abs(d - diameter_mm) < 0.001 and abs(p - pitch_mm) < 0.001:
                return n
        for entry in self._raw_data["fine"]:
            d, p, n = entry
            if abs(d - diameter_mm) < 0.001 and abs(p - pitch_mm) < 0.001:
                return n
        return None

    # ── Suggestion ─────────────────────────────────────────────────────

    def suggest_preset(self, radius_mm):
        """Suggest a diameter and coarse pitch by face radius (mm).

        Returns (diameter_mm, pitch_mm).
        """
        detected_diameter = radius_mm * 2.0
        for d in self.diameters:
            if d >= detected_diameter - 0.001:
                # First (largest) pitch for this diameter
                pitches = self.pitches_for(d)
                if pitches:
                    return (d, pitches[0][0])
                return (d, 1.5)
        return (detected_diameter, 1.5)