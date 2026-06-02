# -*- coding: utf-8 -*-
"""Live thread-preview manager — :class:`ThreadPreview`.

Owns the temporary Coin3D ``SoSeparator`` that is injected into the
active 3D view.  Recomputes geometry and replaces the scene subtree on
every :meth:`ThreadPreview.update` call.
"""

import FreeCADGui as Gui
from pivy import coin

from .helix_line import make_helix_line
from .profile_line import make_profile_line


class ThreadPreview:
    """Manages a temporary Coin3D overlay in the active 3D view.

    Call :meth:`update` to draw/re-draw the preview.
    Call :meth:`remove` to hide it.
    """

    def __init__(self):
        self._sep = None  # root SoSeparator we inject into the scene
        self._attached = False

    # ── Public API ────────────────────────────────────────────────

    def update(self, face_analysis, *, diameter, pitch, length, offset,
               is_external, is_reversed, left_handed=False,
               profile_id="iso68_1", clearance=0.05):
        """Draw or update the preview overlay."""
        if not face_analysis.ok:
            self.remove()
            return

        axis = face_analysis.axis
        cyl_radius = face_analysis.radius
        edges = face_analysis.edges

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
        helix_sep = make_helix_line(
            axis, origin, pitch, length, cyl_radius,
            left_handed=left_handed, helix_reversed=helix_reversed,
        )
        sep.addChild(helix_sep)

        # Profile cross-section (cyan)
        profile_sep = make_profile_line(
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
        """Return the root ``SoSeparator`` of the active 3D view."""
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
