# -*- coding: utf-8 -*-
"""Local sketch frame helper used by builder, runout and preview modules."""

import math

import FreeCAD as App


def build_local_frame(helix_dir):
    """Return ``(radial_basis, rotation)`` for a sketch placed along helix_dir.

    Orientation: sketch Y → ``helix_dir``, sketch X → plane right.
    """
    if abs(helix_dir.z) < 0.9999:
        rad = App.Vector(-helix_dir.y, helix_dir.x, 0.0).normalize()
    else:
        rad = App.Vector(1.0, 0.0, 0.0).normalize()

    tangent = helix_dir.cross(rad).normalize()
    rad = tangent.cross(helix_dir).normalize()

    rot_y = App.Rotation(App.Vector(0, 1, 0), helix_dir)
    cur_x = rot_y.multVec(App.Vector(1, 0, 0))
    angle_rad = math.atan2(
        helix_dir.dot(cur_x.cross(rad)),
        cur_x.dot(rad)
    )
    rot_fix = App.Rotation(helix_dir, math.degrees(angle_rad))
    final_rot = rot_fix.multiply(rot_y)

    return rad, final_rot
