# -*- coding: utf-8 -*-
"""Unified registry for thread preset tables.

Allows:
    - Register a preset table via the @register_preset_table decorator
    - Retrieve a table by profile_id
    - List all registered tables
    - Get profile_id by table type ("metric", "inch", ...)
"""


class PresetRegistry:
    """Registry of thread preset tables.

    Each table is an instance of a class inheriting AbstractPresetTable,
    registered by its profile_id.
    """

    def __init__(self):
        self._tables = {}       # profile_id -> AbstractPresetTable
        self._type_map = {}     # table_type -> profile_id

    # ── Registration ────────────────────────────────────────────────

    def register(self, table):
        """Register a preset table.

        Parameters
        ----------
        table : AbstractPresetTable
            Instance of a preset table.
        """
        pid = table.profile_id
        self._tables[pid] = table
        self._type_map[table.table_type] = pid

    # ── Access by profile_id ───────────────────────────────────────

    def get(self, profile_id):
        """Return the preset table for profile_id, or None."""
        return self._tables.get(profile_id)

    def __getitem__(self, profile_id):
        """table_registry["iso68_1"] -> MetricPresetTable"""
        return self._tables[profile_id]

    def __contains__(self, profile_id):
        return profile_id in self._tables

    # ── Access by type ─────────────────────────────────────────────

    def get_by_type(self, table_type):
        """Return the preset table by type ("metric", "inch", ...).

        Returns None if the type is not registered.
        """
        pid = self._type_map.get(table_type)
        if pid is None:
            return None
        return self._tables.get(pid)

    def profile_id_for_type(self, table_type):
        """Return profile_id by table type, or None."""
        return self._type_map.get(table_type)

    # ── Lists ─────────────────────────────────────────────────────

    @property
    def all_tables(self):
        """list[AbstractPresetTable] — all registered tables."""
        return list(self._tables.values())

    @property
    def all_profile_ids(self):
        """list[str] — all registered profile_ids."""
        return list(self._tables.keys())

    @property
    def all_table_types(self):
        """list[str] — all registered table types."""
        return list(self._type_map.keys())

    # ── Convenience methods for UI ──────────────────────────────────────

    def get_preset_names(self, profile_id):
        """Return the list of preset names for profile_id, or empty list."""
        table = self._tables.get(profile_id)
        if table is None:
            return []
        return table.preset_names

    def find_preset(self, profile_id, *args, **kwargs):
        """Delegate preset search to the table for profile_id.

        Returns None if profile_id is not found.
        """
        table = self._tables.get(profile_id)
        if table is None:
            return None
        return table.find_preset(*args, **kwargs)

    def suggest_preset(self, profile_id, *args, **kwargs):
        """Delegate preset suggestion to the table for profile_id.

        Returns None if profile_id is not found.
        """
        table = self._tables.get(profile_id)
        if table is None:
            return None
        return table.suggest_preset(*args, **kwargs)


# ═══════════════════════════════════════════════════════════════════
# Global registry instance
# ═══════════════════════════════════════════════════════════════════

GLOBAL_REGISTRY = PresetRegistry()


def register_preset_table(table_cls):
    """Decorator to register a preset table class.

    Usage:
        @register_preset_table
        class MetricPresetTable(AbstractPresetTable):
            ...
    """
    instance = table_cls()
    GLOBAL_REGISTRY.register(instance)
    return table_cls