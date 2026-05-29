# -*- coding: utf-8 -*-
"""Base class for thread preset tables.

Subclass defines:
    - profile_id   — string identifier (matches profiles/base.py)
    - table_type   — table type ("metric", "inch", "pipe", ...)
    - label        — human-readable name
    - _raw_data    — raw preset data

Optional override methods:
    - find_preset(diameter, pitch) -> str|None
    - suggest_preset(radius_mm) -> tuple
"""

from abc import ABC, abstractmethod


class AbstractPresetTable(ABC):
    """Base class for a thread preset table.

    Class attributes (overridden in subclasses):
        profile_id  — string identifier (e.g. "iso68_1")
        table_type  — table type (e.g. "metric", "inch")
        label       — human-readable name (e.g. "ISO 724 (Metric)")

    Instance attributes:
        _raw_data   — raw preset data (structure depends on subclass)
    """

    profile_id = "abstract"
    table_type = "abstract"
    label = "Abstract"

    def __init__(self):
        self._raw_data = self._build_raw_data()

    # ── Abstract method ──────────────────────────────────────────

    @abstractmethod
    def _build_raw_data(self):
        """Build raw preset data.

        Called in __init__.  Data structure depends on the subclass.
        """
        ...

    # ── Properties for UI ────────────────────────────────────────────

    @property
    @abstractmethod
    def preset_names(self):
        """list[str] — names of all presets for the dropdown."""
        ...

    # ── Search and suggestion ─────────────────────────────────────────────

    def find_preset(self, *args, **kwargs):
        """Find a preset name by parameters.

        Returns str (preset name) or None.
        """
        return None

    def suggest_preset(self, radius_mm):
        """Suggest a preset by face radius (mm).

        Returns a tuple of parameters specific to the table type,
        or None if no suggestion is available.
        """
        return None

    # ── Thread working depth ─────────────────────────────────────

    @staticmethod
    def thread_depth_factor():
        """Working depth factor: h_work = factor * pitch.

        Default is 5√3/16 ≈ 0.541266 (ISO 68-1 / ASME B1.1).
        """
        return 0.541265877365  # 5 * sqrt(3) / 16