# -*- coding: utf-8 -*-
"""Thread presets for various standards.

Single access point to preset tables via PresetRegistry.

All data is stored in profiles/presets/*.py.
Each thread type is a separate file with a class inheriting AbstractPresetTable,
registered via the @register_preset_table decorator.

Adding a new thread type:
    1. Create profiles/presets/my_standard.py
    2. Define a class MyPresets(AbstractPresetTable)
    3. Import the module in profiles/presets/__init__.py
    4. Done — presets automatically appear in the registry
"""

from profiles.presets import PresetRegistry, AbstractPresetTable
from profiles.presets.registry import GLOBAL_REGISTRY

# ═══════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════

# Global registry (already populated when profiles.presets is imported)
registry = GLOBAL_REGISTRY

# Thread working depth: 5/8 × H = 5√3/16 × P ≈ 0.541266 × P
THREAD_DEPTH_FACTOR = 0.541265877365  # 5 * sqrt(3) / 16


def get_table(profile_id):
    """Return the preset table for profile_id, or None."""
    return registry.get(profile_id)


def get_table_by_type(table_type):
    """Return the preset table by type ("metric", "inch", ...), or None."""
    return registry.get_by_type(table_type)


def profile_id_for_type(table_type):
    """Return profile_id by table type, or None."""
    return registry.profile_id_for_type(table_type)


def all_tables():
    """list[AbstractPresetTable] — all registered tables."""
    return registry.all_tables


def all_profile_ids():
    """list[str] — all registered profile_ids."""
    return registry.all_profile_ids


def all_table_types():
    """list[str] — all registered table types."""
    return registry.all_table_types


# ═══════════════════════════════════════════════════════════════════
# Convenience functions for metric threads (most common case)
# ═══════════════════════════════════════════════════════════════════

def _metric_table():
    """Return MetricPresetTable, or None."""
    return registry.get_by_type("metric")


def metric_diameters():
    """list[float] — unique metric diameters."""
    table = _metric_table()
    if table is None:
        return []
    return table.diameters


def metric_pitches_for(diameter_mm):
    """list[(pitch_mm, name)] — pitches for the given diameter."""
    table = _metric_table()
    if table is None:
        return []
    return table.pitches_for(diameter_mm)


def find_metric_preset(diameter_mm, pitch_mm):
    """Find a metric preset name, or None."""
    table = _metric_table()
    if table is None:
        return None
    return table.find_preset(diameter_mm, pitch_mm)


def suggest_metric_preset(radius_mm):
    """Suggest a metric preset by face radius (mm).

    Returns (diameter_mm, pitch_mm).
    """
    table = _metric_table()
    if table is None:
        return (radius_mm * 2.0, 1.5)
    return table.suggest_preset(radius_mm)


# ═══════════════════════════════════════════════════════════════════
# Convenience functions for inch threads
# ═══════════════════════════════════════════════════════════════════

def _inch_table():
    """Return InchPresetTable, or None."""
    return registry.get_by_type("inch")


def inch_presets():
    """dict[name] -> (d_inch, tpi) — all inch presets."""
    table = _inch_table()
    if table is None:
        return {}
    return table.all_presets


def find_inch_preset(diameter_inch, tpi):
    """Find an inch preset name, or None."""
    table = _inch_table()
    if table is None:
        return None
    return table.find_preset(diameter_inch, tpi)


def suggest_inch_preset(radius_mm):
    """Suggest an inch preset by face radius (mm).

    Returns (preset_name, diameter_inch, tpi).
    """
    table = _inch_table()
    if table is None:
        from translations import translate
        detected_inch = radius_mm * 2.0 / 25.4
        return (translate("Custom", "— Custom —"), detected_inch, 20)
    return table.suggest_preset(radius_mm)
