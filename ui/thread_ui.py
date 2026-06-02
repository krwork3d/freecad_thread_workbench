# -*- coding: utf-8 -*-


"""UI assembly for the Thread Workbench task panel — public entry point."""

from ui.layout import build_form as setup_ui

__all__ = ["setup_ui"]

# Re-export for backward compatibility with thread_dialog.py
# The original function signature is preserved:
#   setup_ui(thread_mode, on_preset, on_custom, on_edge_to_edge, on_create, on_pitch_mm_changed)
