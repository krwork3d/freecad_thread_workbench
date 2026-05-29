# -*- coding: utf-8 -*-
"""Thread geometry construction inside PartDesign::Body.

Isolates FreeCAD-specific logic (sketches, helices, chamfers) from UI.
"""

import math

import FreeCAD as App
import FreeCADGui as Gui
import Part

from translations import translate
from profiles import PROFILE_REGISTRY


# ═══════════════════════════════════════════════════════════════════
# Analysis of the selected cylindrical face
# ═══════════════════════════════════════════════════════════════════

class FaceAnalysis:
    """Result of analysing a selected cylindrical face."""

    __slots__ = (
        'ok', 'error',
        'face_ref',    # (doc_object, sub_name)
        'body',        # PartDesign::Body
        'radius',
        'axis',        # App.Vector (normalised)
        'edges',       # [(t_along_axis, edge_index, center), ...] — sorted
    )

    def __init__(self):
        self.ok = False
        self.error = ""
        self.face_ref = None
        self.body = None
        self.radius = 0.0
        self.axis = None
        self.edges = []

    @staticmethod
    def from_selection():
        """Analyse the current selection and return a FaceAnalysis."""
        result = FaceAnalysis()

        sel = Gui.Selection.getSelectionEx()
        if not sel:
            result.error = translate("err_nothing_selected",
                                     "Nothing selected.")
            return result

        obj = sel[0].Object
        subs = sel[0].SubElementNames
        if not subs:
            result.error = translate("err_no_subelement",
                                     "Could not determine selected sub-element.")
            return result

        sub_name = subs[0]
        try:
            face = obj.getSubObject(sub_name)
        except Exception:
            result.error = translate("err_cannot_read_face",
                                     "Cannot read face.")
            return result

        if not (hasattr(face, "Surface") and hasattr(face.Surface, "Radius")):
            result.error = translate("err_not_cylindrical",
                                     "Selected face is not cylindrical.")
            return result

        # Find the PartDesign::Body
        body = obj
        while body and body.TypeId != 'PartDesign::Body':
            body = getattr(body, 'getParentGeoFeatureGroup', lambda: None)()

        if not body:
            result.error = translate("err_not_in_body",
                                     "Object is not inside a PartDesign::Body.")
            return result

        surf = face.Surface
        axis = surf.Axis.normalize()
        radius = surf.Radius

        # Circular edges
        edge_params = []  # (t_along_axis, edge_index, center)
        for i, edge in enumerate(face.Edges):
            curve = edge.Curve
            if hasattr(curve, "Radius") and hasattr(curve, "Center"):
                ec = curve.Center
                t = ec.dot(axis)
                edge_params.append((t, i + 1, ec))

        edge_params.sort(key=lambda x: x[0])

        result.ok = True
        result.face_ref = (obj, sub_name)
        result.body = body
        result.radius = radius
        result.axis = axis
        result.edges = edge_params
        return result


# ═══════════════════════════════════════════════════════════════════
# Sketch orientation calculation
# ═══════════════════════════════════════════════════════════════════

def _build_local_frame(helix_dir):
    """Return (origin, rotation) for the sketch given the helix direction.

    Orientation: sketch Y → helix_dir, sketch X → plane right.
    """
    # Basis: perpendicular to helix_dir
    if abs(helix_dir.z) < 0.9999:
        rad = App.Vector(-helix_dir.y, helix_dir.x, 0.0).normalize()
    else:
        rad = App.Vector(1.0, 0.0, 0.0).normalize()

    tangent = helix_dir.cross(rad).normalize()
    rad = tangent.cross(helix_dir).normalize()

    # Rotation: Y → helix_dir, X → rad
    rot_y = App.Rotation(App.Vector(0, 1, 0), helix_dir)
    cur_x = rot_y.multVec(App.Vector(1, 0, 0))
    angle_rad = math.atan2(
        helix_dir.dot(cur_x.cross(rad)),
        cur_x.dot(rad)
    )
    rot_fix = App.Rotation(helix_dir, math.degrees(angle_rad))
    final_rot = rot_fix.multiply(rot_y)

    return rad, final_rot



def _build_helix(body, sketch, pitch, length, label, left_handed=False,
                 reversed=False):
    """Create a PartDesign::SubtractiveHelix. Return the helix object."""
    helix = body.newObject("PartDesign::SubtractiveHelix", label)
    helix.Profile = (sketch, ['', ])
    helix.ReferenceAxis = (sketch, ['V_Axis'])
    helix.Pitch = pitch
    helix.Height = length + pitch * 0.5
    helix.Mode = 0
    helix.LeftHanded = left_handed
    helix.Reversed = reversed
    return helix


def _add_runout(body, far_end, neg_cut_dir, pitch, cyl_radius, is_external,
                diameter, profile):
    """Add an additive revolution of a rectangular profile at the far end
    to close the groove cleanly — same principle as Fusion 360.

    A rectangle from r_root to r_surface, width = pitch, is revolved 360°
    as an additive feature.  This fills the cross-section of the groove
    with a simple cylindrical band.
    """
    _rad, rot = _build_local_frame(neg_cut_dir)

    sketch = body.Document.addObject(
        "Sketcher::SketchObject",
        profile.label(diameter, pitch, "RunoutProfile"))
    body.addObject(sketch)
    sketch.Placement = App.Placement(far_end, rot)

    h_work = profile._working_depth(pitch)
    r_surface, r_root = profile._surface_radii(cyl_radius, h_work, is_external)

    pts = [
        App.Vector(r_surface, 0.0,      0.0),
        App.Vector(r_root,    0.0,      0.0),
        App.Vector(r_root,    pitch,    0.0),
        App.Vector(r_surface, pitch,    0.0),
    ]

    for i in range(len(pts)):
        sketch.addGeometry(
            Part.LineSegment(pts[i], pts[(i + 1) % len(pts)]), False)

    body.Document.recompute()

    revolution = body.newObject("PartDesign::Revolution",
                                profile.label(diameter, pitch, "Runout"))
    revolution.Profile = (sketch, ['', ])
    revolution.ReferenceAxis = (sketch, ['V_Axis'])
    revolution.Angle = 360.0

    body.Document.recompute()
    sketch.Visibility = False
    return revolution


# ═══════════════════════════════════════════════════════════════════
# Main function: create a thread
# ═══════════════════════════════════════════════════════════════════

def create_thread(
    face_analysis,   # FaceAnalysis
    *,
    diameter,        # nominal diameter (for label)
    pitch,
    length,          # thread length; None/0 → edge-to-edge
    offset,
    is_external,
    is_reversed,
    left_handed=False,
    runout=True,     # smooth runout at the far end (Fusion 360 style)
    profile_id="iso68_1",  # profile identifier from PROFILE_REGISTRY
):
    """Create a thread on a cylindrical face inside a PartDesign::Body.

    This function does *not* manage transactions — the caller should
    wrap it in doc.openTransaction/commitTransaction as needed.
    If something goes wrong it raises RuntimeError.
    """
    if not face_analysis.ok:
        raise RuntimeError(face_analysis.error)

    body = face_analysis.body
    axis = face_analysis.axis
    cyl_radius = face_analysis.radius
    edges = face_analysis.edges

    doc = body.Document

    # ── Helix direction ──
    if len(edges) >= 2:
        t_start = edges[0][0]
        t_other = edges[-1][0]
        natural_dir = axis if t_other > t_start else -axis
    else:
        natural_dir = axis

    # Internal thread profile goes outward (r_root > r_surface),
    # so the helix direction must be inverted relative to external.
    effective_reversed = is_reversed if is_external else not is_reversed
    cut_dir = -natural_dir if effective_reversed else natural_dir
    helix_reversed = (cut_dir.dot(axis) < 0)

    # ── Start point ──
    ec_start = edges[0][2]                     # already on cylinder axis
    origin = ec_start + cut_dir * (offset - pitch * 0.5)

    # ── Auto-length «edge-to-edge» ──
    if not length or length <= 0:
        if len(edges) >= 2:
            length = abs(edges[-1][0] - edges[0][0])
        else:
            raise RuntimeError(
                translate("err_not_enough_edges",
                          "Not enough edges for auto-length. "
                          "Specify thread length manually."))

    # ── Resolve profile ──
    profile_class = PROFILE_REGISTRY.get(profile_id)
    if profile_class is None:
        raise RuntimeError(
            translate("err_unknown_profile",
                      "Unknown thread profile: {pid}").format(pid=profile_id))
    profile = profile_class()

    # ── Sketch ──
    rad, final_rot = _build_local_frame(axis)

    sketch = doc.addObject("Sketcher::SketchObject",
                           profile.label(diameter, pitch, "Profile"))
    body.addObject(sketch)
    sketch.Placement = App.Placement(origin, final_rot)

    pts = profile.build_profile(pitch, cyl_radius, is_external)

    for i in range(len(pts)):
        p1 = pts[i]
        p2 = pts[(i + 1) % len(pts)]
        sketch.addGeometry(Part.LineSegment(p1, p2), False)
    doc.recompute()

    # ── Helix ──
    try:
        helix = _build_helix(body, sketch, pitch, length,
                             profile.label(diameter, pitch, "Helix"),
                             left_handed, helix_reversed)
        doc.recompute()
    except Exception as e:
        # If helix fails, sketch & chamfer stay — transaction will roll back
        raise RuntimeError(
            translate("err_helix_failed",
                      "Failed to create helix: {e}").format(e=e)) from e

    sketch.Visibility = False

    # ── Runout (smooth end, additive revolution) ──
    if runout:
        # far_end = 1 pitch past the helix tip, so runout extends beyond
        helix_tip = origin + cut_dir * (length + pitch * 0.5)
        far_end = helix_tip + cut_dir * pitch
        neg_cut_dir = -cut_dir
        _add_runout(body, far_end, neg_cut_dir, pitch, cyl_radius,
                    is_external, diameter, profile)

    return helix


def _label(diameter, pitch, role):
    """Build a human-readable name: 'Thread M16×1.25 Helix' etc.

    Kept for backward compatibility; new code should use profile.label().
    """
    d_str = f"{diameter:.2f}".rstrip('0').rstrip('.')
    p_str = f"{pitch:.3f}".rstrip('0').rstrip('.')
    return f"Thread M{d_str}×{p_str} {role}"
