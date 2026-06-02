# -*- coding: utf-8 -*-
"""Coin3D scene-node builder for the helix path."""

import math

import FreeCAD as App
from pivy import coin


def make_helix_line(axis, origin, pitch, length, radius,
                    left_handed=False, helix_reversed=False,
                    segments_per_pitch=48):
    """Build a ``SoSeparator`` representing the helix path as an orange line."""
    n_segments = max(int(length / pitch * segments_per_pitch), 24)

    # Direction along the helix
    cut_dir = -axis if helix_reversed else axis

    pts = []
    for i in range(n_segments + 1):
        t = length * i / n_segments
        angle = 2.0 * math.pi * t / pitch
        if left_handed:
            angle = -angle
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = t
        v = App.Vector(x, y, z)
        # Rotate to align with axis
        rot = App.Rotation(App.Vector(0, 0, 1), cut_dir)
        v = rot.multVec(v)
        v = v + origin
        pts.append((v.x, v.y, v.z))

    coords = coin.SoCoordinate3()
    coords.point.setValues(pts)

    draw_style = coin.SoDrawStyle()
    draw_style.style = coin.SoDrawStyle.LINES
    draw_style.lineWidth = 2

    line_set = coin.SoLineSet()
    line_set.numVertices.setValue(n_segments + 1)

    # Colour — bright orange for visibility
    material = coin.SoMaterial()
    material.diffuseColor = (1.0, 0.5, 0.0)  # orange
    material.transparency = 0.0
    material.ambientColor = (0.2, 0.1, 0.0)

    sep = coin.SoSeparator()
    sep.addChild(material)
    sep.addChild(draw_style)
    sep.addChild(coords)
    sep.addChild(line_set)

    return sep
