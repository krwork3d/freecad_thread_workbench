# -*- coding: utf-8 -*-
"""Thread profile per ASME B1.1 standard (Unified Thread — inch threads).

Truncated trapezoid with a rounded root for external threads.
"""

import math
import FreeCAD as App

from freecad.ThreadWorkbench.threads.base import AbstractThreadProfile, _register


# Exact theoretical UNR root radius factor per ASME B1.1: H/8 = 0.108253175
_ROOT_RADIUS_FACTOR = 0.108253175


@_register
class ASME_B1_1Profile(AbstractThreadProfile):
    """ASME B1.1 — Unified inch profile with a rounded root."""

    PROFILE_ID = "asme_b11"
    LABEL = "ASME B1.1 (Unified Inch)"

    def build_profile(self, pitch, cyl_radius, is_external):
        h_work = self._working_depth(pitch)
        r_surface, r_root = self._surface_radii(cyl_radius, h_work, is_external)

        if is_external:
            return self._build_external_rounded(pitch, r_surface, r_root)
        else:
            return self._make_flat_root_points(pitch, r_surface, r_root)

    @staticmethod
    def _build_external_rounded(pitch, r_surface, r_root):
        """Build external thread profile per exact ASME B1.1 (UNR) geometry."""
        R = _ROOT_RADIUS_FACTOR * pitch

        # Standard crest flat width is P/8.
        # Groove boundaries on the cylinder surface:
        y0 = pitch / 16.0                 # crest left edge
        y3 = 15.0 * pitch / 16.0          # crest flat edge
        y_center = pitch / 2.0            # axial centre of the root

        # 1. Height of the fundamental 60° triangle
        H = pitch * (math.sqrt(3.0) / 2.0)

        # 2. True UNR root depth from major diameter per standard (11/16 * H)
        h_unr = (11.0 / 16.0) * H

        # 3. Radial coordinate of the deepest point of the root arc
        r_unr_bottom = r_surface - h_unr

        # 4. Chord points (B and C) approximating the bottom of the root arc.
        # The inscribed circle chord width at 30° junction angle is exactly R.
        # Due to chord approximation, its radial coordinate rises by R * (1 - cos(15°))
        r_chord = r_unr_bottom + R * (1.0 - math.cos(math.radians(15.0)))

        # Half-width of the chord along Y is R * sin(15°)
        dy_chord = R * math.sin(math.radians(15.0))
        by = y_center - dy_chord
        cy = y_center + dy_chord

        # 5. Junction points of the arc with straight flanks (A and D).
        # Per standard, the arc transitions to the flank at 30° from vertical.
        # Height of the junction point above the root bottom is R * (1 - cos(30°))
        r_touch = r_unr_bottom + R * (1.0 - math.cos(math.radians(30.0)))

        # Y-offset of the junction point from centre is R * sin(30°)
        dy_touch = R * math.sin(math.radians(30.0))  # equals 0.5 * R
        ay = y_center - dy_touch
        dy_val = y_center + dy_touch

        # Build the final point array with no gaps or kinks
        points = [
            App.Vector(r_surface, y0, 0.0),   # crest left (60° flank start)
            App.Vector(r_touch, ay, 0.0),     # A — line-to-arc junction
            App.Vector(r_chord, by, 0.0),     # B — left edge of bottom chord
            App.Vector(r_chord, cy, 0.0),     # C — right edge of bottom chord
            App.Vector(r_touch, dy_val, 0.0), # D — arc-to-right-flank junction
            App.Vector(r_surface, y3, 0.0),   # crest right (60° flank end)
        ]

        return points
