# -*- coding: utf-8 -*-
"""Coin3D scene-node builder for the thread profile cross-section."""

from pivy import coin

from freecad.ThreadWorkbench.threads import PROFILE_REGISTRY

from ..frame import build_local_frame


def make_profile_line(axis, center, pitch, radius, offset,
                      is_external, profile_id="iso68_1"):
    """Build a ``SoSeparator`` showing the thread profile cross-section."""
    profile_class = PROFILE_REGISTRY.get(profile_id)
    if profile_class is None:
        return coin.SoSeparator()
    profile = profile_class()
    pts = profile.build_profile(pitch, radius, is_external)

    # Transform profile points to 3D space at the start position
    cut_dir = axis
    origin = center + cut_dir * (offset - pitch * 0.5)

    # Rotation: sketch Y → cut_dir, sketch X → perpendicular (shared helper).
    _, final_rot = build_local_frame(cut_dir)

    world_pts = []
    for p in pts:
        v = final_rot.multVec(p)
        v = v + origin
        world_pts.append((v.x, v.y, v.z))

    # Close the polygon
    if world_pts:
        world_pts.append(world_pts[0])

    coords = coin.SoCoordinate3()
    coords.point.setValues(world_pts)

    draw_style = coin.SoDrawStyle()
    draw_style.style = coin.SoDrawStyle.LINES
    draw_style.lineWidth = 2

    line_set = coin.SoLineSet()
    line_set.numVertices.setValue(len(world_pts))

    material = coin.SoMaterial()
    material.diffuseColor = (0.0, 0.6, 1.0)  # cyan/blue
    material.transparency = 0.0
    material.ambientColor = (0.0, 0.2, 0.3)

    sep = coin.SoSeparator()
    sep.addChild(material)
    sep.addChild(draw_style)
    sep.addChild(coords)
    sep.addChild(line_set)

    return sep
