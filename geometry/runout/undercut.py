# -*- coding: utf-8 -*-
"""Undercut runout — subtractive thread relief groove (DIN 76-2 / ISO 3508)."""

import FreeCAD as App
import Part

from ..frame import build_local_frame


def build_undercut(body, thread_end, fwd_dir, pitch, cyl_radius, is_external,
                   diameter, profile, length_factor=3.0, clearance=0.25):
    """Subtractive thread relief undercut (DIN 76-2 / ISO 3508 style).

    A circumferential groove cut immediately past the full-profile thread
    end, providing tap/die clearance and a clean thread termination.

    Geometry (DIN 76-2 form A, simplified):
        Internal: groove widens the bore OUTWARD by ``h_work + clearance``
                  for ``length_factor * pitch`` axially.
        External: groove necks the shaft INWARD by the same amount
                  (DIN 76-1 equivalent).

    Defaults (``length_factor=3``, ``clearance=0.25 mm``) match DIN 76-2
    “normal” form for typical metric sizes (M6…M30).
    """
    h_work = profile._working_depth(pitch)
    if is_external:
        r_min = cyl_radius - h_work - clearance
        r_max = cyl_radius + 0.01
    else:
        r_min = cyl_radius - 0.01
        r_max = cyl_radius + h_work + clearance

    axial_len = pitch * length_factor

    # Sketch.Y = fwd_dir, sketch placed at thread_end. The relief groove
    # occupies the LAST `axial_len` of the thread feature region: profile
    # local y ∈ [-axial_len, 0] maps to world range
    # [thread_end - axial_len*fwd_dir, thread_end] — i.e. the groove ends
    # exactly at the user-specified thread end and extends BACK into the
    # thread, replacing the last few turns with a smooth wider/narrower
    # ring (DIN 76-2 form A).
    _, rot = build_local_frame(fwd_dir)

    sketch = body.Document.addObject(
        "Sketcher::SketchObject",
        profile.label(diameter, pitch, "RunoutUndercutProfile"))
    body.addObject(sketch)
    sketch.Placement = App.Placement(thread_end, rot)

    pts = [
        App.Vector(r_min, -axial_len, 0.0),
        App.Vector(r_max, -axial_len, 0.0),
        App.Vector(r_max, 0.0,        0.0),
        App.Vector(r_min, 0.0,        0.0),
    ]

    for i in range(len(pts)):
        sketch.addGeometry(
            Part.LineSegment(pts[i], pts[(i + 1) % len(pts)]), False)

    body.Document.recompute()

    groove = body.newObject("PartDesign::Groove",
                            profile.label(diameter, pitch, "RunoutUndercut"))
    groove.Profile = (sketch, ['', ])
    groove.ReferenceAxis = (sketch, ['V_Axis'])
    groove.Angle = 360.0

    body.Document.recompute()
    sketch.Visibility = False
    return groove
