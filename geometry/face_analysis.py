# -*- coding: utf-8 -*-
"""Selection analysis for a cylindrical face inside a PartDesign::Body."""

import FreeCADGui as Gui

from translations import translate


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
        """Analyse the current selection and return a :class:`FaceAnalysis`."""
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
