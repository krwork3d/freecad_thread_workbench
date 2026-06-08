# -*- coding: utf-8 -*-
"""Pre-cut cylindrical Groove that compensates stock-vs-nominal mismatch."""

import FreeCAD as App
import Part

from .frame import build_local_frame


def build_pre_cut(body, doc, ec_start, cut_dir, axis,
                  offset, pitch,
                  stock_radius, target_radius,
                  is_external, label,
                  axial_len):
    """Build a cylindrical Groove that brings the stock surface to ``target_radius``.

    For external: removes the ring from ``target_radius`` to ``stock_radius``
    (reduces shaft to nominal diameter minus clearance).
    For internal: removes the ring from ``stock_radius`` to ``target_radius``
    (enlarges bore to nominal minor plus clearance).

    The pre-cut covers from the helix origin for ``axial_len`` in ``cut_dir``.
    """
    axial_start = offset - pitch * 0.5

    # Sketch plane: Y = cut_dir (axial), X = radial from rotation axis
    _, rot = build_local_frame(cut_dir)
    pre_origin = ec_start + cut_dir * axial_start

    sketch = doc.addObject("Sketcher::SketchObject", label + "Profile")
    body.addObject(sketch)
    sketch.Placement = App.Placement(pre_origin, rot)

    # The clearance is already baked into target_radius by the caller.
    # Here we just need a small overlap beyond stock for clean boolean.
    eps = 0.01  # boolean overlap
    if is_external:
        # External: cut from target (inner) to stock + eps (outer)
        r_inner = target_radius
        r_outer = stock_radius + eps
    else:
        # Internal: cut from stock - eps (inner) to target (outer)
        r_inner = stock_radius - eps
        r_outer = target_radius

    pts = [
        App.Vector(r_inner, 0.0,       0.0),
        App.Vector(r_outer, 0.0,       0.0),
        App.Vector(r_outer, axial_len, 0.0),
        App.Vector(r_inner, axial_len, 0.0),
    ]

    for i in range(len(pts)):
        sketch.addGeometry(
            Part.LineSegment(pts[i], pts[(i + 1) % len(pts)]), False)

    doc.recompute()

    groove = body.newObject("PartDesign::Groove", label)
    groove.Profile = (sketch, ['', ])
    groove.ReferenceAxis = (sketch, ['V_Axis'])
    groove.Angle = 360.0

    doc.recompute()
    sketch.Visibility = False
    return groove
