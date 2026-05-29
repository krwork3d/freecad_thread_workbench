# -*- coding: utf-8 -*-
"""Thread profiles for various standards.

Each profile is a class inheriting AbstractThreadProfile,
with a method build_profile(pitch, cyl_radius, is_external) → list[App.Vector].

Available profiles are registered in PROFILE_REGISTRY.

Preset tables are in profiles.presets.PresetRegistry.
"""

from profiles.base import AbstractThreadProfile, PROFILE_REGISTRY
from profiles.iso68_1 import ISO68_1Profile
from profiles.asme_b11 import ASME_B1_1Profile

# Preset registry (dimension tables)
from profiles.presets import PresetRegistry, register_preset_table, AbstractPresetTable

__all__ = [
    "AbstractThreadProfile",
    "PROFILE_REGISTRY",
    "ISO68_1Profile",
    "ASME_B1_1Profile",
    "PresetRegistry",
    "register_preset_table",
    "AbstractPresetTable",
]