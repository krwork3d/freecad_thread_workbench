# -*- coding: utf-8 -*-
"""Thread preset tables for various standards.

Each thread type is a separate module with a class inheriting
AbstractPresetTable.  Registration happens via the @register_preset_table
decorator in the PresetRegistry.

Adding a new thread type:
    1. Create a file profiles/presets/my_standard.py
    2. Define a class MyPresets(AbstractPresetTable)
    3. Import the module in this __init__.py
"""

from profiles.presets.registry import PresetRegistry, register_preset_table
from profiles.presets.base import AbstractPresetTable

# Import preset modules (they self-register via the decorator)
from profiles.presets import metric
from profiles.presets import inch

__all__ = [
    "PresetRegistry",
    "register_preset_table",
    "AbstractPresetTable",
]