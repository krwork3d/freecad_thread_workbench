# -*- coding: utf-8 -*-
"""Thread feature orchestrator — :func:`create_thread`.

Wires together:

* :class:`~geometry.face_analysis.FaceAnalysis` — selection input.
* :func:`~geometry.precut.build_pre_cut` — stock-vs-nominal compensation.
* :func:`~geometry.helix.build_helix` — main subtractive helix.
* :mod:`geometry.runout` — end-of-thread features.
"""

import FreeCAD as App
import Part

from freecad.ThreadWorkbench.translations import translate
from freecad.ThreadWorkbench.threads import PROFILE_REGISTRY

from .frame import build_local_frame
from .helix import build_helix
from .precut import build_pre_cut
from . import runout as runout_module


def create_thread(
    face_analysis,   # FaceAnalysis
    *,
    diameter,        # nominal diameter (defines thread depth)
    pitch,
    length,          # thread length; None/0 → edge-to-edge
    offset,
    is_external,
    is_reversed,
    left_handed=False,
    runout="pocket",  # runout mode: "none", "pocket", "tapered"
    profile_id="iso68_1",  # profile identifier from PROFILE_REGISTRY
    clearance=0.05,  # pre-cut clearance when stock ≠ nominal (mm)
):
    """Create a thread on a cylindrical face inside a PartDesign::Body.

    This function does *not* manage transactions — the caller should
    wrap it in ``doc.openTransaction``/``commitTransaction`` as needed.
    If something goes wrong it raises :class:`RuntimeError`.
    """
    if not face_analysis.ok:
        raise RuntimeError(face_analysis.error)

    body = face_analysis.body
    axis = face_analysis.axis
    cyl_radius = face_analysis.radius
    edges = face_analysis.edges

    doc = body.Document

    # ── Thread direction ──
    # Always from the chosen start edge (edges[0]) to the other edge (edges[-1]).
    # The user selects which edge to start from; the thread goes to the other edge.
    if len(edges) >= 2:
        edge_vector = edges[-1][2] - edges[0][2]
        # Project onto cylinder axis to get direction along the axis
        if edge_vector.dot(axis) >= 0:
            thread_dir = axis
        else:
            thread_dir = -axis
    else:
        thread_dir = axis

    # is_reversed flips the direction (start from the other edge)
    cut_dir = -thread_dir if is_reversed else thread_dir

    # ── Start point ──
    ec_start = edges[0][2]                     # already on cylinder axis
    origin = ec_start + cut_dir * (offset - pitch * 0.5)

    # ── Auto-length «edge-to-edge» ──
    if not length or length <= 0:
        if len(edges) >= 2:
            # Base length is the distance between edges.
            # Adjust for offset: negative offset (chamfer) extends the thread,
            # positive offset shortens it, so the thread always reaches the far edge.
            base_length = abs(edges[-1][0] - edges[0][0])
            length = base_length - offset
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

    # ── Pre-cut cylinder (if stock radius differs from nominal) ──────
    # When a thread is cut on oversize stock (e.g. M12 on ∓13 shaft) or
    # undersize bore (e.g. M10 in −8 hole), first remove the excess
    # material with a cylindrical Groove so the thread profile operates
    # on a correctly-sized surface.
    #
    # The `clearance` (default 0.05 mm) is subtracted from the nominal
    # major (external) or added to the nominal minor (internal) to
    # produce a slight relief for assembly fit.
    nominal_radius = diameter / 2.0
    h_work = profile._working_depth(pitch)

    if is_external:
        # Thread crests at nominal_radius - clearance
        target_radius = nominal_radius - clearance
    else:
        # Thread crests (= bore wall) at nominal_minor + clearance
        target_radius = (nominal_radius - h_work) + clearance

    # Compute helix height early (needed for pre-cut extent).
    # y_back = 15P/16 for all standard threads (ISO 68-1 / ASME B1.1).
    y_back_est = 15.0 * pitch / 16.0
    if runout == "tapered":
        main_helix_height = max(length + pitch * 0.5 - y_back_est, pitch * 0.5)
    else:
        main_helix_height = length + pitch * 0.5

    # Pre-cut axial length depends on runout mode:
    #  - "pocket": must reach far_end (offset+length+P from ec_start).
    #              In edge-to-edge mode, far_end may extend beyond the
    #              cylinder face (to mate with adjacent features like a
    #              bolt head), so pre-cut must cover that extended length.
    #  - "tapered": must cover the conical fade zone (+P*0.5)
    #  - others: just the main helix sweep (path + last profile overshoot)
    if runout == "pocket":
        pre_cut_axial_len = main_helix_height + pitch
    elif runout == "tapered":
        pre_cut_axial_len = main_helix_height + y_back_est + pitch * 0.5
    else:
        pre_cut_axial_len = main_helix_height + y_back_est

    pre_cut_depth = abs(cyl_radius - target_radius)
    if pre_cut_depth > 0.01:  # threshold: only pre-cut if Δr > 0.01 mm
        build_pre_cut(
            body, doc, ec_start, cut_dir, axis,
            offset, pitch,
            cyl_radius, target_radius,
            is_external,
            profile.label(diameter, pitch, "PreCut"),
            pre_cut_axial_len,
        )
        doc.recompute()
        # Thread profile now operates on the target surface
        cyl_radius = target_radius

    # ── Sketch ──
    # Orient the sketch along cut_dir (not axis) so the helix always
    # starts at `origin` and grows along cut_dir — matching the live
    # preview and the other runout features (pre-cut, tapered, undercut).
    # This avoids relying on PartDesign Helix ``Reversed``, which shifts
    # the spiral start to the opposite end of the path.
    rad, final_rot = build_local_frame(cut_dir)

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

    # ── Main helix height ──
    # Already pre-computed above (before pre-cut) using y_back_est = 15P/16.
    # Refine for tapered mode with the actual profile y_back if it differs.
    if runout == "tapered":
        y_back = max(p.y for p in pts)
        if abs(y_back - y_back_est) > 1e-6:
            main_helix_height = max(length + pitch * 0.5 - y_back, pitch * 0.5)

    # ── Helix ──
    # Reversed is always False: the sketch is already oriented along
    # cut_dir, so the helix grows from `origin` in the correct direction.
    try:
        helix = build_helix(body, sketch, pitch, main_helix_height,
                            profile.label(diameter, pitch, "Helix"),
                            left_handed, False)
        doc.recompute()
    except Exception as e:
        # If helix fails, sketch & runout stay — transaction will roll back
        raise RuntimeError(
            translate("err_helix_failed",
                      "Failed to create helix: {e}").format(e=e)) from e

    sketch.Visibility = False

    # ── Runout (smooth end / fill) ──
    # The PartDesign helix sweeps a profile of pitch-tall cross-section,
    # so the visible groove on the cylinder extends ONE FULL PITCH past
    # the helix path tip. Anchor the runout's forward edge at this true
    # groove-tip position.
    #
    # For subtractive runouts (tapered, undercut), we clamp to the
    # cylinder's far face to avoid features in empty space (typical for
    # auto-length external threads where the helix path already runs
    # flush with the face).
    #
    # For additive runouts (pocket), we allow the fill to extend beyond
    # the cylinder boundary so it can properly close the groove and mate
    # with adjacent features (e.g., bolt head). This is essential for
    # edge-to-edge threads where the thread must transition smoothly
    # into a non-cylindrical feature.

    # Runout direction: from start edge to end edge (same as cut_dir)
    ec_start = edges[0][2]
    ec_end = edges[-1][2]
    helix_dir = cut_dir  # Use the same direction as the helix
    back_dir = -helix_dir

    cyl_end_dist = (ec_end - ec_start).dot(helix_dir)
    groove_tip_dist = offset + length + pitch  # along helix_dir from ec_start

    # For additive runout (pocket), we want the fill to start at the
    # actual thread end (groove_tip) regardless of cylinder boundary,
    # so it properly closes the groove and can extend to mate with
    # adjacent features (e.g., bolt head). For subtractive runouts
    # (tapered, undercut), we still clamp to the cylinder boundary
    # to avoid features in empty space.
    if runout == "pocket":
        forward_dist = groove_tip_dist
    else:
        if cyl_end_dist > 0.0:
            forward_dist = min(groove_tip_dist, cyl_end_dist)
        else:
            forward_dist = groove_tip_dist

    far_end = ec_start + helix_dir * forward_dist

    # Position of the user-specified thread end (for undercut anchor).
    # This is the boundary where the full-profile thread terminates,
    # placed in the same 3D direction the helix actually grows.
    # For pocket runout, we don't clamp to cylinder boundary to allow
    # the fill to extend to adjacent features (e.g., bolt head).
    thread_end_dist = offset + length
    if runout != "pocket" and cyl_end_dist > 0.0:
        thread_end_dist = min(thread_end_dist, cyl_end_dist)
    thread_end = ec_start + helix_dir * thread_end_dist

    runout_module.apply(
        body, runout,
        far_end=far_end, back_dir=back_dir,
        thread_end=thread_end,
        origin=origin, cut_dir=helix_dir, axis=axis,
        pitch=pitch, main_helix_height=main_helix_height,
        cyl_radius=cyl_radius,
        is_external=is_external, diameter=diameter, profile=profile,
        left_handed=left_handed,
    )

    return helix
