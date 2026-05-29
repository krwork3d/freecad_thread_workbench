# -*- coding: utf-8 -*-
"""Base class for all thread profiles and the profile registry."""

import math
import FreeCAD as App


# Registry: profile_id → profile class
PROFILE_REGISTRY = {}


def _register(profile_class):
    """Decorator/function to register a profile in the registry."""
    pid = getattr(profile_class, "PROFILE_ID", None)
    if pid is None:
        pid = profile_class.__name__
    PROFILE_REGISTRY[pid] = profile_class
    return profile_class


class AbstractThreadProfile:
    """Base class for a thread profile.

    Class attributes (overridden in subclasses):
        PROFILE_ID  — string identifier (e.g. "iso68_1", "asme_b11")
        LABEL       — human-readable name (e.g. "ISO 68-1 (Metric)")
        ANGLE_DEG   — profile angle in degrees (60° for all standard threads)
    """

    PROFILE_ID = "abstract"
    LABEL = "Abstract"
    ANGLE_DEG = 60.0

    # -----------------------------------------------------------------
    # Geometric constants (common to ISO 68-1 / ASME B1.1)
    # -----------------------------------------------------------------
    # H = (√3/2) × P — height of the fundamental triangle
    # h_work = 5/8 × H = (5√3/16) × P ≈ 0.541266 × P — working depth
    # crest flat = H/8 from tip → width P/8
    # root flat  = H/4 from base → width P/4
    # -----------------------------------------------------------------

    @staticmethod
    def _H(pitch):
        """Height of the fundamental triangle."""
        return pitch * (math.sqrt(3.0) / 2.0)

    @staticmethod
    def _working_depth(pitch):
        """Working depth h = 5/8 × H."""
        return 5.0 / 8.0 * pitch * (math.sqrt(3.0) / 2.0)

    # -----------------------------------------------------------------
    # API for subclasses
    # -----------------------------------------------------------------

    def build_profile(self, pitch, cyl_radius, is_external):
        """Build the thread profile points.

        Parameters
        ----------
        pitch : float
            Thread pitch in mm.
        cyl_radius : float
            Cylindrical face radius in mm.
        is_external : bool
            True — external thread (bolt), False — internal (nut).

        Returns
        -------
        list[App.Vector]
            Closed polygon of 4+ points for the subtractive-helix sketch.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement build_profile()"
        )

    def label(self, diameter, pitch, role):
        """Build a human-readable name: 'Thread M16×1.25 Helix'."""
        d_str = f"{diameter:.2f}".rstrip("0").rstrip(".")
        p_str = f"{pitch:.3f}".rstrip("0").rstrip(".")
        return f"Thread M{d_str}×{p_str} {role}"

    # -----------------------------------------------------------------
    # Helper methods for subclasses
    # -----------------------------------------------------------------

    @staticmethod
    def _make_flat_root_points(pitch, r_surface, r_root):
        """Build 4 points of a truncated trapezoid with a flat root.

        Returns [App.Vector, App.Vector, App.Vector, App.Vector]
        in order: crest_start, root_start, root_end, crest_end.
        """
        y0 = pitch / 16.0          # crest flat edge
        y1 = 3.0 * pitch / 8.0     # root flat start
        y2 = 5.0 * pitch / 8.0     # root flat end
        y3 = 15.0 * pitch / 16.0   # crest flat edge

        return [
            App.Vector(r_surface, y0, 0.0),
            App.Vector(r_root,    y1, 0.0),
            App.Vector(r_root,    y2, 0.0),
            App.Vector(r_surface, y3, 0.0),
        ]

    @staticmethod
    def _surface_radii(cyl_radius, h_work, is_external, eps=0.01):
        """Compute r_surface and r_root considering external/internal.

        For external: groove goes INWARD (r_root < r_surface).
        For internal: groove goes OUTWARD from the hole (r_root > r_surface).
        """
        if is_external:
            return cyl_radius + eps, cyl_radius - h_work
        else:
            return cyl_radius - eps, cyl_radius + h_work