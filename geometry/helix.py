# -*- coding: utf-8 -*-
"""PartDesign::SubtractiveHelix primitive used by the thread builder."""


def build_helix(body, sketch, pitch, height, label,
                left_handed=False, reversed=False):
    """Create a PartDesign::SubtractiveHelix with explicit path height.

    ``height`` is the raw value written into ``helix.Height`` (the helix
    path length); the caller decides whether to add the +pitch/2 lead-in
    overhang or to shorten it for a tapered runout.
    """
    helix = body.newObject("PartDesign::SubtractiveHelix", label)
    helix.Profile = (sketch, ['', ])
    helix.ReferenceAxis = (sketch, ['V_Axis'])
    helix.Pitch = pitch
    helix.Height = height
    helix.Mode = 0
    helix.LeftHanded = left_handed
    helix.Reversed = reversed
    return helix
