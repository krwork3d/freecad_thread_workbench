# -*- coding: utf-8 -*-
"""Pocket runout — additive cylindrical fill.

Closes the helical groove at the far end of an external thread by
revolving a thin band flush with the cylinder surface.
"""

import FreeCAD as App
import Part

from ..frame import build_local_frame

# Enable debug logging
DEBUG = True


def fill_pocket(body, far_end, back_dir, pitch, cyl_radius, is_external,
                diameter, profile):
    """Additive cylindrical fill at the far end of the thread.

    Revolves a rectangle (``r_min..r_max`` radially, ``pitch`` axially)
    360° to close the groove cross-section with a smooth band.
    The fill extends BACK from ``far_end`` into the thread body and
    covers one full turn of the helix — enough to close the groove at
    every angular position.
    """
    h_work = profile._working_depth(pitch)
    r_surface, r_root = profile._surface_radii(cyl_radius, h_work, is_external)

    r_min = min(r_surface, r_root) 
    r_max = max(r_surface, r_root) - 0.01

    # Y = back_dir → revolution extends BACK into the thread body
    _, rot = build_local_frame(back_dir)

    sketch = body.Document.addObject(
        "Sketcher::SketchObject",
        profile.label(diameter, pitch, "RunoutFillProfile"))
    body.addObject(sketch)
    sketch.Placement = App.Placement(far_end, rot)

    axial_len = pitch  # full turn coverage
    pts = [
        App.Vector(r_min, 0.0,       0.0),
        App.Vector(r_max, 0.0,       0.0),
        App.Vector(r_max, axial_len, 0.0),
        App.Vector(r_min, axial_len, 0.0),
    ]

    for i in range(len(pts)):
        sketch.addGeometry(
            Part.LineSegment(pts[i], pts[(i + 1) % len(pts)]), False)

    body.Document.recompute()

    revolution = body.newObject("PartDesign::Revolution",
                                profile.label(diameter, pitch, "RunoutFill"))
    revolution.Profile = (sketch, ['', ])
    revolution.ReferenceAxis = (sketch, ['V_Axis'])
    revolution.Angle = 360.0

    body.Document.recompute()
    sketch.Visibility = False
    return revolution
