# -*- coding: utf-8 -*-
"""Thread profile per BS 21 / ISO 228-1 (BSP — Whitworth 55°).

Rounded crest and rounded root with radius r = 0.137329·P.

The Whitworth thread form has:
- Thread angle: 55° (each flank 27.5° from the perpendicular to the axis,
  i.e. 27.5° from the radial direction)
- Crest rounding radius: r = 0.137329·P
- Root rounding radius:  r = 0.137329·P
- Working depth: h = 2/3 × H, where H = P / (2 × tan(27.5°))

The rounding arcs are tangent to the straight flanks.  The radius to a
tangent point is perpendicular to the flank, therefore it makes 62.5°
with the radial axis (= 27.5° with the thread axis).  This 62.5° angle
is the one used to locate the tangent points.

With r = 0.137329·P and h = 2/3·H the straight flanks between the two
tangent arcs come out at exactly 55° — the three constants are mutually
consistent by design of the Whitworth standard.

Geometry (external thread, subtractive groove profile in the r-y plane)::

    Y=0              P/2               P
     |  crest arc   |   root arc      |
     |    ___       |       ___       |
     |   /   \\     |     //   \\     |
     |  /     \\    |    //     \\    |
     | /       \\   |   //       \\   |
     |/         \\__|__//         \\__|
     |            \\ | /            |
     |             \\|/             |
    r_surface      r_root         r_surface
"""

import math
import FreeCAD as App

from freecad.ThreadWorkbench.threads.base import AbstractThreadProfile, _register


# ═══════════════════════════════════════════════════════════════════
# Constants for Whitworth 55° thread form
# ═══════════════════════════════════════════════════════════════════

_HALF_ANGLE_RAD = math.radians(27.5)
_SIN_HA = math.sin(_HALF_ANGLE_RAD)   # ≈ 0.461749  (sin 27.5° = cos 62.5°)
_COS_HA = math.cos(_HALF_ANGLE_RAD)   # ≈ 0.887011  (cos 27.5° = sin 62.5°)
_H_FACTOR = 1.0 / (2.0 * math.tan(_HALF_ANGLE_RAD))   # ≈ 0.960491

# Working depth = 2/3 × H (Whitworth standard)
_WORK_FACTOR = (2.0 / 3.0) * _H_FACTOR  # ≈ 0.640327

# Crest/root rounding radius factor per standard
_R_FACTOR = 0.137329

# Number of segments for arc approximation
_ARC_SEGMENTS = 12

# ═══════════════════════════════════════════════════════════════════
# Profile class
# ═══════════════════════════════════════════════════════════════════


@_register
class BSPProfile(AbstractThreadProfile):
    """BSP / Whitworth — 55° profile with rounded crest and rounded root.

    The arc radius (0.137329 × P) is the defining characteristic of
    the Whitworth thread form per BS 21 / ISO 228-1.
    """

    PROFILE_ID = "bsp"
    LABEL = "BSP (Whitworth 55°)"
    ANGLE_DEG = 55.0

    @staticmethod
    def _H(pitch):
        """Height of the fundamental 55° triangle."""
        return pitch * _H_FACTOR

    @staticmethod
    def _working_depth(pitch):
        """Working depth h = 2/3 × H (Whitworth)."""
        return pitch * _WORK_FACTOR

    def build_profile(self, pitch, cyl_radius, is_external):
        """Build the Whitworth 55° profile points.

        Returns a closed polygon approximating the rounded crest and root
        with straight-line flank segments.
        """
        h_work = self._working_depth(pitch)
        r_surface, r_root = self._surface_radii(cyl_radius, h_work, is_external)
        return _make_whitworth_profile(pitch, r_surface, r_root)

    def label(self, diameter, pitch, role):
        """Build a human-readable name."""
        return f"Thread BSP {role}"


# ═══════════════════════════════════════════════════════════════════
# Profile geometry generation
# ═══════════════════════════════════════════════════════════════════

# Tangent-point angle measured from the radial axis.
# The flank makes 27.5° with the radial direction (perpendicular to the
# axis), so the radius to the tangent point — being normal to the flank —
# makes 62.5° with the radial axis (= 27.5° with the thread axis).
_TANGENT_RAD = math.radians(90.0 - 27.5)   # 62.5°


def _make_whitworth_profile(pitch, r_surface, r_root):
    """Build polygon for Whitworth 55° rounded thread profile.

    The profile (one pitch, subtractive groove) consists of:

    1. Left flank  — straight line from crest to root
    2. Root arc    — concave, radius r, tangent to both flanks
    3. Right flank — straight line from root to crest
    4. Crest arc   — convex, radius r, tangent to both flanks
                     (wraps across the y = 0 / y = P boundary)

    Both arcs use the Whitworth rounding radius r = 0.137329·P and are
    tangent to the 55° flanks.  The tangent points lie at 62.5° from the
    radial axis (27.5° from the thread axis), where the arc radius is
    perpendicular to the flank.

    Parameters
    ----------
    pitch : float
        Thread pitch in mm.
    r_surface : float
        Radial position of the crest surface (major diameter / 2).
    r_root : float
        Radial position of the thread root (minor diameter / 2).

    Returns
    -------
    list[App.Vector]
        Closed polygon points in the r-y plane spanning one pitch.
    """
    r = _R_FACTOR * pitch          # rounding radius
    a = _TANGENT_RAD               # 62.5° from radial

    # Arc centres ---------------------------------------------------------
    # Crest arc: convex, apex at (r_surface, 0), centre inset by r.
    cr_c_r = r_surface - r
    cr_c_y = 0.0
    # Root arc: concave, nadir at (r_root, P/2), centre offset outward by r.
    rt_c_r = r_root + r
    rt_c_y = pitch / 2.0

    # Tangent-point coordinates ------------------------------------------
    # cos(62.5°) = sin(27.5°) = _SIN_HA ; sin(62.5°) = cos(27.5°) = _COS_HA
    cos_a = _SIN_HA   # ≈ 0.461749
    sin_a = _COS_HA   # ≈ 0.887011

    # Crest right tangent: angle +62.5°, y = +r·sin a  (near y = 0)
    crest_right = App.Vector(cr_c_r + r * cos_a, r * sin_a, 0.0)
    # Crest left tangent: angle -62.5°, y = -r·sin a  → wrap to P - r·sin a
    crest_left = App.Vector(cr_c_r + r * cos_a, pitch - r * sin_a, 0.0)
    # Root lower tangent: angle 242.5°, y = P/2 - r·sin a
    root_lower = App.Vector(rt_c_r - r * cos_a, rt_c_y - r * sin_a, 0.0)
    # Root upper tangent: angle 117.5°, y = P/2 + r·sin a
    root_upper = App.Vector(rt_c_r - r * cos_a, rt_c_y + r * sin_a, 0.0)

    # Assemble the closed polygon ----------------------------------------
    # Traversal: crest_right → (left flank) → root_lower → (root arc) →
    # root_upper → (right flank) → crest_left → (crest arc, wraps) → close.
    pts = [crest_right, root_lower]
    pts.extend(_arc_points(rt_c_r, rt_c_y, r,
                           math.pi + a, math.pi - a,
                           _ARC_SEGMENTS, include_end=True))
    pts.append(crest_left)
    pts.extend(_arc_points(cr_c_r, cr_c_y, r,
                           -a, a,
                           _ARC_SEGMENTS, wrap_pitch=pitch,
                           include_end=False))
    return pts


def _arc_points(c_r, c_y, radius, theta_start, theta_end, n,
                wrap_pitch=None, include_end=True):
    """Sample points along a circular arc.

    Generates points at fractions i/n (i = 1..n) of the sweep from
    ``theta_start`` to ``theta_end``.  The start point is never emitted
    (it is assumed to already be the previous polygon vertex); the end
    point is emitted only when ``include_end`` is True.

    Parameters
    ----------
    c_r, c_y : float
        Arc centre coordinates.
    radius : float
        Arc radius.
    theta_start, theta_end : float
        Start/end angles in radians (from the +r axis).
    n : int
        Number of segments the arc is divided into.
    wrap_pitch : float or None
        If given, negative Y values are wrapped by adding ``wrap_pitch``
        (used for the crest arc that straddles the y = 0 / y = P seam).
    include_end : bool
        Whether to emit the end point (theta_end).
    """
    sweep = theta_end - theta_start
    last = n if include_end else n - 1
    pts = []
    for i in range(1, last + 1):
        theta = theta_start + (i / n) * sweep
        r = c_r + radius * math.cos(theta)
        y = c_y + radius * math.sin(theta)
        if wrap_pitch is not None and y < 0.0:
            y += wrap_pitch
        pts.append(App.Vector(r, y, 0.0))
    return pts
