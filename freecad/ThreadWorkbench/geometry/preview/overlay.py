# -*- coding: utf-8 -*-
"""Live thread-preview manager — :class:`ThreadPreview`.

Owns the temporary Coin3D ``SoSeparator`` that is injected into the
active 3D view.  Recomputes geometry and replaces the scene subtree on
every :meth:`ThreadPreview.update` call.
"""

import FreeCADGui as Gui
from pivy import coin

from freecad.ThreadWorkbench.geometry.thread_frame import resolve_thread_frame
from freecad.ThreadWorkbench.threads import PROFILE_REGISTRY

from .helix_line import make_helix_line
from .profile_line import make_profile_line
from .surface import make_thread_surface


class ThreadPreview:
    """Manages a temporary Coin3D overlay in the active 3D view.

    Call :meth:`update` to draw/re-draw the preview.
    Call :meth:`remove` to hide it.
    """

    # Transparency applied to the host body while preview is visible.
    _BODY_TRANSPARENCY = 75

    def __init__(self):
        self._sep = None  # root SoSeparator we inject into the scene
        self._attached = False
        self._body = None            # body made translucent during preview
        self._body_transparency = 0  # saved original transparency

    # ── Public API ────────────────────────────────────────────────

    def update(self, face_analysis, *, diameter, pitch, length, offset,
               is_external, is_reversed, left_handed=False,
               profile_id="iso68_1", clearance=0.05):
        """Draw or update the preview overlay."""
        if not face_analysis.ok:
            self.remove()
            return

        axis = face_analysis.axis
        stock_radius = face_analysis.radius
        edges = face_analysis.edges

        if not edges:
            self.remove()
            return

        # Resolve thread frame using shared logic (same as builder.create_thread)
        try:
            frame = resolve_thread_frame(axis, edges, is_reversed, offset, pitch, length)
        except RuntimeError:
            self.remove()
            return

        cut_dir = frame['cut_dir']
        origin = frame['origin']
        length = frame['length']
        helix_reversed = (cut_dir.dot(axis) < 0)

        # ── Resolve effective surface radius from nominal diameter ──
        # Mirrors builder.create_thread pre-cut logic: when stock radius
        # differs from nominal, the thread actually sits on target_radius.
        # Using it here makes the preview reflect diameter changes.
        profile_class = PROFILE_REGISTRY.get(profile_id)
        cyl_radius = stock_radius
        if profile_class is not None:
            profile_tmp = profile_class()
            h_work = profile_tmp._working_depth(pitch)
            nominal_radius = diameter / 2.0
            if is_external:
                target_radius = nominal_radius - clearance
            else:
                target_radius = (nominal_radius - h_work) + clearance
            # Apply pre-cut only when the stock differs from target by
            # more than the threshold (matches builder.py).
            if abs(stock_radius - target_radius) > 0.01:
                cyl_radius = target_radius

        # Build the scene
        sep = coin.SoSeparator()

        # ── Shaded swept thread-groove surface (translucent) ──
        # This is the "solid cut preview" — like FreeCAD's hole preview.
        if profile_class is not None:
            profile = profile_tmp
            profile_pts = profile.build_profile(pitch, cyl_radius, is_external)
            surface_sep = make_thread_surface(
                axis, origin, pitch, length, cyl_radius,
                profile_pts,
                is_external=is_external,
                left_handed=left_handed,
                helix_reversed=helix_reversed,
            )
            sep.addChild(surface_sep)

        # ── Helix path line (orange) ──
        helix_sep = make_helix_line(
            axis, origin, pitch, length, cyl_radius,
            left_handed=left_handed, helix_reversed=helix_reversed,
        )
        sep.addChild(helix_sep)

        # ── Profile cross-section (cyan) ──
        profile_sep = make_profile_line(
            axis, origin, pitch, cyl_radius,
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

        # Make the host body translucent so the thread groove shows
        # through it (like FreeCAD's hole preview).
        self._apply_body_transparency(face_analysis.body)

        # Replace or attach
        self._attach(sep)

    def remove(self):
        """Remove the preview overlay from the scene."""
        self._restore_body_transparency()
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

    # ── Host-body transparency ────────────────────────────────────

    def _apply_body_transparency(self, body):
        """Make ``body`` semi-transparent while the preview is shown."""
        if body is None:
            return
        # Restore any previously dimmed body first.
        self._restore_body_transparency()
        self._body = body
        try:
            self._body_transparency = body.ViewObject.Transparency
            body.ViewObject.Transparency = self._BODY_TRANSPARENCY
        except Exception:
            self._body = None
            self._body_transparency = 0

    def _restore_body_transparency(self):
        """Restore the original transparency of the host body."""
        if self._body is None:
            return
        try:
            self._body.ViewObject.Transparency = self._body_transparency
        except Exception:
            pass
        self._body = None
        self._body_transparency = 0
