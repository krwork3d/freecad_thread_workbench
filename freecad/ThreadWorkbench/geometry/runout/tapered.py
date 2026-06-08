# -*- coding: utf-8 -*-
"""Tapered runout — conical SubtractiveHelix.

Continues the main helix with an extra fraction of a turn whose
profile gradually shifts radially by exactly the working depth, so the
groove smoothly fades out into the cylinder surface.
"""

import math

import FreeCAD as App
import Part

from ..frame import build_local_frame


def build_tapered(body, origin, cut_dir, axis, pitch, cyl_radius,
                  main_helix_height, is_external, diameter, profile,
                  left_handed, runout_turns=0.5):
    """Real (smooth) thread runout via a conical PartDesign::SubtractiveHelix.

    Continues the main helix with an additional ``runout_turns`` revolutions
    where the cut-profile radius is gradually shifted by the working depth,
    so the groove smoothly emerges from the cylinder surface and fades to
    zero depth — the same technique used by FreeCAD's ``screw_maker``
    module (angled helix with cone angle ``atan(2·H·17/24 / P)``).

    The runout sketch is placed at the helix tip and rotated around the axis
    so its profile-zero matches the angular phase of the main helix end,
    giving a continuous groove across the join.
    """
    h_work = profile._working_depth(pitch)
    axial_len = pitch * runout_turns

    # Cone angle: over `axial_len` along the axis, profile shifts radially
    # by exactly h_work (fades the groove out fully).
    cone_angle_deg = math.degrees(math.atan2(h_work, axial_len))

    # Angular phase at the end of the main helix.
    # PartDesign helix with LeftHanded=False is right-handed in 3D: the
    # profile rotates +CCW around the advance direction (right-hand rule
    # with thumb along cut_dir → fingers point in the rotation direction).
    turns = main_helix_height / pitch
    phase_deg = (turns * 360.0) % 360.0
    if left_handed:
        phase_deg = -phase_deg

    helix_tip = origin + cut_dir * main_helix_height

    # Build local frame with sketch Y aligned to cut_dir (helix advance),
    # then rotate around cut_dir by phase_deg to align with main-helix end.
    _, rot_align = build_local_frame(cut_dir)
    rot_phase = App.Rotation(cut_dir, phase_deg)
    final_rot = rot_phase.multiply(rot_align)

    sketch = body.Document.addObject(
        "Sketcher::SketchObject",
        profile.label(diameter, pitch, "RunoutTaperProfile"))
    body.addObject(sketch)
    sketch.Placement = App.Placement(helix_tip, final_rot)

    pts = profile.build_profile(pitch, cyl_radius, is_external)
    for i in range(len(pts)):
        sketch.addGeometry(
            Part.LineSegment(pts[i], pts[(i + 1) % len(pts)]), False)
    body.Document.recompute()

    helix = body.newObject("PartDesign::SubtractiveHelix",
                           profile.label(diameter, pitch, "RunoutTaper"))
    helix.Profile = (sketch, ['', ])
    helix.ReferenceAxis = (sketch, ['V_Axis'])
    helix.Pitch = pitch
    helix.Height = axial_len
    helix.Mode = 0
    # External: cone widens (profile shifts outward) → groove fades out.
    # Internal: cone narrows (profile shifts toward axis) → groove fades
    # into the bore.  PartDesign Helix Angle > 0 widens in growth direction.
    helix.Angle = cone_angle_deg if is_external else -cone_angle_deg
    helix.LeftHanded = left_handed
    helix.Reversed = False  # sketch Y is already aligned with cut_dir

    body.Document.recompute()
    sketch.Visibility = False
    return helix
