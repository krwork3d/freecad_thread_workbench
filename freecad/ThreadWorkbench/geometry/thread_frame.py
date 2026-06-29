# -*- coding: utf-8 -*-
"""Common thread frame resolution — shared between builder and preview.

Provides :func:`resolve_thread_frame` which computes the thread direction,
origin point, and effective length from face analysis edges and user parameters.
"""

from freecad.ThreadWorkbench.translations import translate


def resolve_thread_frame(
    axis,        # cylinder axis (App.Vector, normalized)
    edges,       # list of (t_along_axis, edge_index, center) — sorted by t
    is_reversed, # bool — flip the start edge
    offset,      # float — axial offset from start edge
    pitch,       # float — thread pitch
    length,      # float or None — thread length (0/None → edge-to-edge)
):
    """Compute thread direction, origin, and effective length.

    This is the shared logic between :func:`~geometry.builder.create_thread`
    and :class:`~geometry.preview.ThreadPreview`.

    Parameters
    ----------
    axis : App.Vector
        Cylinder axis (normalised).
    edges : list[tuple]
        Sorted list of (t_along_axis, edge_index, center_point).
    is_reversed : bool
        If True, start from the far edge instead of the near edge.
    offset : float
        Axial offset from the start edge (mm). Negative = chamfer extension.
    pitch : float
        Thread pitch (mm).
    length : float or None
        Desired thread length. If falsy or <= 0, auto-length (edge-to-edge)
        is used.

    Returns
    -------
    dict with keys:
        thread_dir   — App.Vector, direction from start to end edge
        cut_dir      — App.Vector, actual cutting direction (may be flipped)
        ec_start     — App.Vector, center of the start edge
        ec_end       — App.Vector, center of the end edge (or None if single edge)
        origin       — App.Vector, helix start point (includes offset adjustment)
        length       — float, effective thread length (always positive)

    Raises
    ------
    RuntimeError
        If there are not enough edges for auto-length calculation.
    """
    if not edges:
        raise RuntimeError(
            translate("err_not_enough_edges",
                      "Not enough edges for thread frame calculation."))

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
    ec_end = edges[-1][2] if len(edges) >= 2 else None
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

    return {
        'thread_dir': thread_dir,
        'cut_dir': cut_dir,
        'ec_start': ec_start,
        'ec_end': ec_end,
        'origin': origin,
        'length': length,
    }
