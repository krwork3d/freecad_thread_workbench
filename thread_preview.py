# -*- coding: utf-8 -*-
"""Coin3D preview overlay for thread parameters.

Draws a temporary 3D helix line in the active view to visualise
thread parameters *without* creating any document objects.

Usage
-----
    from thread_preview import ThreadPreview

    preview = ThreadPreview()
    preview.update(analysis, diameter=10, pitch=1.5, ...)
    preview.remove()
"""

import math

import FreeCAD as App
import FreeCADGui as Gui
from pivy import coin

from profiles import PROFILE_REGISTRY


# ═══════════════════════════════════════════════════════════════════
# Coin3D helpers
# ═══════════════════════════════════════════════════════════════════

def _make_helix_line(axis, origin, pitch, length, radius,
                     left_handed=False, helix_reversed=False,
                     segments_per_pitch=48):
    """Build a SoLineSet representing the helix path.

    Returns a SoSeparator with a coloured line.
    """
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

    # Build Coin3D line set
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


def _make_profile_line(axis, center, pitch, radius, offset,
                       is_external, profile_id="iso68_1"):
    """Build a SoLineSet showing the thread profile cross-section.

    Returns a SoSeparator with a coloured line.
    """
    profile_class = PROFILE_REGISTRY.get(profile_id)
    if profile_class is None:
        return coin.SoSeparator()
    profile = profile_class()
    pts = profile.build_profile(pitch, radius, is_external)

    # Transform profile points to 3D space at the start position
    cut_dir = axis
    origin = center + cut_dir * (offset - pitch * 0.5)

    # Build rotation: sketch Y → cut_dir, sketch X → perpendicular
    if abs(cut_dir.z) < 0.9999:
        rad = App.Vector(-cut_dir.y, cut_dir.x, 0.0).normalize()
    else:
        rad = App.Vector(1.0, 0.0, 0.0).normalize()
    tangent = cut_dir.cross(rad).normalize()
    rad = tangent.cross(cut_dir).normalize()
    rot_y = App.Rotation(App.Vector(0, 1, 0), cut_dir)
    cur_x = rot_y.multVec(App.Vector(1, 0, 0))
    angle_rad = math.atan2(
        cut_dir.dot(cur_x.cross(rad)),
        cur_x.dot(rad)
    )
    final_rot = App.Rotation(cut_dir, math.degrees(angle_rad)).multiply(rot_y)

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


# ═══════════════════════════════════════════════════════════════════
# Preview manager
# ═══════════════════════════════════════════════════════════════════

class ThreadPreview:
    """Manages a temporary Coin3D overlay in the active 3D view.

    Call ``update()`` to draw/re-draw the preview.
    Call ``remove()`` to hide it.
    """

    def __init__(self):
        self._sep = None  # root SoSeparator we inject into the scene
        self._attached = False

    # ── Public API ────────────────────────────────────────────────

    def update(self, face_analysis, *, diameter, pitch, length, offset,
               is_external, is_reversed, left_handed=False,
               profile_id="iso68_1"):
        """Draw or update the preview overlay."""
        if not face_analysis.ok:
            self.remove()
            return

        axis = face_analysis.axis
        cyl_radius = face_analysis.radius
        edges = face_analysis.edges
        body = face_analysis.body

        if not edges:
            self.remove()
            return

        # Helix direction
        if len(edges) >= 2:
            t_start = edges[0][0]
            t_other = edges[-1][0]
            natural_dir = axis if t_other > t_start else -axis
        else:
            natural_dir = axis

        effective_reversed = is_reversed if is_external else not is_reversed
        cut_dir = -natural_dir if effective_reversed else natural_dir
        helix_reversed = (cut_dir.dot(axis) < 0)

        ec_start = edges[0][2]
        origin = ec_start + cut_dir * (offset - pitch * 0.5)

        # Auto-length
        if not length or length <= 0:
            if len(edges) >= 2:
                length = abs(edges[-1][0] - edges[0][0])
            else:
                self.remove()
                return

        # Build the scene
        sep = coin.SoSeparator()

        # Helix line (orange)
        helix_sep = _make_helix_line(
            axis, origin, pitch, length, cyl_radius,
            left_handed=left_handed, helix_reversed=helix_reversed,
        )
        sep.addChild(helix_sep)

        # Profile cross-section (cyan)
        profile_sep = _make_profile_line(
            axis, origin, pitch, cyl_radius, offset,
            is_external, profile_id,
        )
        sep.addChild(profile_sep)

        # Axis line (thin grey) — helps orientation
        axis_len = length + pitch
        axis_pts = [
            (origin.x, origin.y, origin.z),
            (origin.x + axis.x * axis_len,
             origin.y + axis.y * axis_len,
             origin.z + axis.z * axis_len),
        ]
        axis_coords = coin.SoCoordinate3()
        axis_coords.point.setValues(axis_pts)
        axis_style = coin.SoDrawStyle()
        axis_style.style = coin.SoDrawStyle.LINES
        axis_style.lineWidth = 1
        axis_material = coin.SoMaterial()
        axis_material.diffuseColor = (0.5, 0.5, 0.5)
        axis_line = coin.SoLineSet()
        axis_line.numVertices.setValue(2)
        axis_sep = coin.SoSeparator()
        axis_sep.addChild(axis_material)
        axis_sep.addChild(axis_style)
        axis_sep.addChild(axis_coords)
        axis_sep.addChild(axis_line)
        sep.addChild(axis_sep)

        # Replace or attach
        self._attach(sep)

    def remove(self):
        """Remove the preview overlay from the scene."""
        self._detach()

    # ── Internal ──────────────────────────────────────────────────

    def _get_scene_graph(self):
        """Return the root SoSeparator of the active 3D view."""
        view = Gui.ActiveDocument.ActiveView
        return view.getViewer().getSceneGraph()

    def _attach(self, sep):
        """Replace current preview with a new one."""
        self._detach()
        try:
            root = self._get_scene_graph()
            root.addChild(sep)
            self._sep = sep
            self._attached = True
        except Exception:
            self._sep = None
            self._attached = False

    def _detach(self):
        """Remove current preview from the scene."""
        if self._attached and self._sep is not None:
            try:
                root = self._get_scene_graph()
                root.removeChild(self._sep)
            except Exception:
                pass
        self._sep = None
        self._attached = False