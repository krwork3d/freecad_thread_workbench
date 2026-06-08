# -*- coding: utf-8 -*-
"""Coin3D preview overlay for thread parameters.

Draws a temporary 3D helix line + profile cross-section + axis line in
the active 3D view, *without* creating any document objects.

Usage
-----
    from geometry import ThreadPreview

    preview = ThreadPreview()
    preview.update(analysis, diameter=10, pitch=1.5, ...)
    preview.remove()
"""

from .overlay import ThreadPreview

__all__ = ["ThreadPreview"]
