# -*- coding: utf-8 -*-
"""Coin3D scene-node builder for the swept thread surface.

Builds a semi-transparent shaded mesh that represents the helical
groove volume — the same kind of "solid cut preview" FreeCAD shows
for holes in the latest versions.

The mesh is a sweep of the thread profile polygon along the helix:
at each station *t* the profile is rotated around the cylinder axis
by the helix twist angle and translated along the cut direction.
"""

import math

import FreeCAD as App
from pivy import coin

from ..frame import build_local_frame


def make_thread_surface(
    axis, origin, pitch, length, cyl_radius,
    profile_pts, *,
    is_external=True, left_handed=False, helix_reversed=False,
    segments_per_pitch=24, max_segments=800,
):
    """Build a ``SoSeparator`` with a shaded swept thread-groove surface.

    Parameters
    ----------
    axis : App.Vector
        Cylinder axis (normalised).
    origin : App.Vector
        Helix start point (already includes offset).
    pitch, length, cyl_radius : float
        Thread geometry.
    profile_pts : list[App.Vector]
        Profile polygon points in sketch-local coords
        (X = radial, Y = along axis, Z = 0).
    is_external : bool
        Affects tint (external = orange, internal = cyan).
    left_handed : bool
        Reverse helix twist.
    helix_reversed : bool
        Cut direction is ``-axis``.
    """
    if not profile_pts or pitch <= 0 or length <= 0:
        return coin.SoSeparator()

    cut_dir = -axis if helix_reversed else axis

    # Local frame at t=0: sketch Y → axis, sketch X → radial.
    _, final_rot = build_local_frame(axis)

    # Profile points in world space, offset from origin at t=0.
    base_pts = [final_rot.multVec(p) for p in profile_pts]
    m = len(base_pts)
    if m < 2:
        return coin.SoSeparator()

    # Station count along the helix.
    n = max(int(length / pitch * segments_per_pitch), 16)
    n = min(n, max_segments)

    twist_sign = -1.0 if left_handed else 1.0

    # Build vertex grid: n stations × m profile points (closed loop).
    coords_list = []
    for i in range(n + 1):
        t = length * i / n
        theta = twist_sign * 2.0 * math.pi * t / pitch
        rot = App.Rotation(axis, math.degrees(theta))
        shift = origin + cut_dir * t
        for j in range(m):
            v = rot.multVec(base_pts[j]) + shift
            coords_list.append((v.x, v.y, v.z))

    coords = coin.SoCoordinate3()
    coords.point.setValues(coords_list)

    # Quad faces between station i and i+1, profile edge j and j+1 (wrap).
    face_index = []
    for i in range(n):
        for j in range(m):
            j2 = (j + 1) % m
            v0 = i * m + j
            v1 = i * m + j2
            v2 = (i + 1) * m + j2
            v3 = (i + 1) * m + j
            face_index.extend([v0, v1, v2, v3, -1])

    indexed = coin.SoIndexedFaceSet()
    indexed.coordIndex.setValues(face_index)

    # Material — translucent tint, like FreeCAD's cut-volume preview.
    if is_external:
        diffuse = (1.0, 0.45, 0.0)      # orange (external / bolt)
    else:
        diffuse = (0.0, 0.55, 1.0)      # cyan (internal / nut)

    material = coin.SoMaterial()
    material.diffuseColor = diffuse
    material.transparency = 0.55
    material.ambientColor = (diffuse[0] * 0.3,
                             diffuse[1] * 0.3,
                             diffuse[2] * 0.3)
    material.emissiveColor = (diffuse[0] * 0.15,
                              diffuse[1] * 0.15,
                              diffuse[2] * 0.15)

    # Shape hints: unknown face type → render both sides (no back-face
    # culling), so the translucent ribbon reads from any angle.
    hints = coin.SoShapeHints()
    hints.vertexOrdering = coin.SoShapeHints.COUNTERCLOCKWISE
    hints.shapeType = coin.SoShapeHints.SOLID
    hints.faceType = coin.SoShapeHints.UNKNOWN_FACE_TYPE
    hints.creaseAngle = math.radians(30.0)

    style = coin.SoDrawStyle()
    style.style = coin.SoDrawStyle.FILLED

    sep = coin.SoSeparator()
    sep.addChild(hints)
    sep.addChild(material)
    sep.addChild(style)
    sep.addChild(coords)
    sep.addChild(indexed)
    return sep
