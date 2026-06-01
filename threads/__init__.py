# -*- coding: utf-8 -*-
"""Thread profiles and preset tables.

Adding a new thread standard
----------------------------
Drop a new sub-package next to this file::

    threads/<my_standard>/
        __init__.py        # may stay empty
        profile.py         # class inheriting AbstractThreadProfile
                           # decorated with @_register
        presets.json       # manifest with profile_id / table_type / label
                           # and grouped preset entries
        presets.py         # (optional) class inheriting AbstractPresetTable
                           # decorated with @register_preset_table; only
                           # needed when type-specific search/suggestion
                           # is required (otherwise base defaults apply)

The registry is populated automatically — no edits to this file or to the
UI are needed.

Adding a new preset to an existing standard
-------------------------------------------
Edit the corresponding ``threads/<standard>/presets.json`` file.  No code
changes required.
"""

import importlib
import os
import pkgutil

from threads.base import (
    AbstractThreadProfile,
    AbstractPresetTable,
    PROFILE_REGISTRY,
)
from threads.registry import (
    PresetRegistry,
    GLOBAL_REGISTRY,
    register_preset_table,
)


# ═══════════════════════════════════════════════════════════════════
# Auto-discovery: import every sub-package's profile/presets modules
# so that the @_register / @register_preset_table decorators populate
# the global registries.
# ═══════════════════════════════════════════════════════════════════

# Modules to attempt within each sub-package, in order.  Profile must come
# first because preset tables sometimes reference profile constants.
_AUTOLOAD_MODULES = ("profile", "presets")


def _autodiscover_standards():
    """Import profile.py / presets.py in every sub-package of ``threads``."""
    pkg_dir = os.path.dirname(__file__)
    for _finder, name, is_pkg in pkgutil.iter_modules([pkg_dir]):
        if not is_pkg:
            continue
        if name.startswith("_"):
            continue
        for module_name in _AUTOLOAD_MODULES:
            try:
                importlib.import_module(f"threads.{name}.{module_name}")
            except ModuleNotFoundError:
                # Optional module (e.g. presets.py absent for profile-only
                # standards): silently skip.
                continue
            except Exception as exc:  # noqa: BLE001
                # Don't let one broken standard kill the whole registry.
                try:
                    import FreeCAD as App
                    App.Console.PrintError(
                        f"[ThreadWorkbench] Failed to load "
                        f"threads.{name}.{module_name}: {exc}\n"
                    )
                except Exception:
                    print(
                        f"[ThreadWorkbench] Failed to load "
                        f"threads.{name}.{module_name}: {exc}"
                    )


_autodiscover_standards()


__all__ = [
    "AbstractThreadProfile",
    "AbstractPresetTable",
    "PROFILE_REGISTRY",
    "PresetRegistry",
    "GLOBAL_REGISTRY",
    "register_preset_table",
]
