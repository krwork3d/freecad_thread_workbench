# -*- coding: utf-8 -*-
"""Inch thread preset table ASME B1.1 (UNC/UNF).

All preset data lives in ``presets.json`` next to this module, organised
the same way the UI consumes it: each size lists the TPI options
available for that diameter, each tagged with its thread class.  This
file only contains type-specific search/suggestion logic — adding or
editing presets is a JSON-only change.

JSON schema for one size entry::

    {
      "label":         "1/4",          # display label (fraction or '#N')
      "diameter_inch": 0.250,
      "options": [
        {"tpi": 20, "class": "UNC"},
        {"tpi": 28, "class": "UNF"}
      ]
    }

Display name is built as ``"{label}-{tpi} {class}"`` (e.g. ``"1/4-20 UNC"``).
The first option for a size is treated as the default suggestion.

Public API (used by the UI):
    - preset_names             -> list[str]
    - all_presets              -> {name: (d_inch, tpi), ...}
    - find_preset(d_inch, tpi) -> str | None
    - suggest_preset(r_mm)     -> (name, d_inch, tpi)
"""

from threads.base import AbstractPresetTable
from threads.registry import register_preset_table


# Floating-point tolerance for diameter comparisons (in inches).
_EPS_INCH = 5e-4


@register_preset_table
class InchPresetTable(AbstractPresetTable):
    """Inch thread preset table ASME B1.1 — data-driven from presets.json."""

    # Identity is read from the manifest; no need to duplicate here.

    # ── Name formatting ──────────────────────────────────────────────

    @staticmethod
    def _fmt_tpi(tpi):
        """Format TPI: 20 → '20', 4.5 → '4.5'."""
        if isinstance(tpi, float) and tpi.is_integer():
            return str(int(tpi))
        return f"{tpi:g}"

    @classmethod
    def _name_for(cls, size, option):
        return f"{size['label']}-{cls._fmt_tpi(option['tpi'])} {option['class']}"

    # ── Public accessors ─────────────────────────────────────────────

    @property
    def preset_names(self):
        """list[str] — every preset name in canonical (size, option) order."""
        return [
            self._name_for(size, opt)
            for size in self.sizes
            for opt in size["options"]
        ]

    @property
    def all_presets(self):
        """dict[name] -> (d_inch, tpi) — flat view of every preset."""
        return {
            self._name_for(size, opt): (size["diameter_inch"], opt["tpi"])
            for size in self.sizes
            for opt in size["options"]
        }

    # ── Search ──────────────────────────────────────────────────────

    def find_preset(self, diameter_inch, tpi):
        """Find a preset name by diameter (inches) and TPI."""
        for size in self.sizes:
            if abs(size["diameter_inch"] - diameter_inch) >= _EPS_INCH:
                continue
            for opt in size["options"]:
                if opt["tpi"] == tpi:
                    return self._name_for(size, opt)
        return None

    # ── Suggestion ──────────────────────────────────────────────────

    def suggest_preset(self, radius_mm):
        """Suggest the nearest inch preset by face radius (mm).

        Returns (preset_name, diameter_inch, tpi).
        """
        from translations import translate

        detected_inch = radius_mm * 2.0 / 25.4
        for size in sorted(self.sizes, key=lambda s: s["diameter_inch"]):
            if size["diameter_inch"] >= detected_inch - _EPS_INCH:
                opt = size["options"][0]  # first option (UNC by convention)
                return (self._name_for(size, opt),
                        size["diameter_inch"],
                        opt["tpi"])
        return (translate("Custom", "— Custom —"), detected_inch, 20)
