# -*- coding: utf-8 -*-
"""Thread runout / end-of-thread features.

Builds the auxiliary PartDesign features that close or fade the helical
groove at the end of a thread:

* :func:`fill_pocket`  — additive Revolution: fills the last full turn
  flush with the cylinder surface (general-purpose smooth end for
  external).
* :func:`build_tapered` — conical SubtractiveHelix that continues the
  main helix and fades its profile to zero depth over the runout span
  (real screw-runout, ``screw_maker2_3`` style; external threads).
* :func:`build_undercut` — subtractive Revolution that cuts a
  circumferential relief groove past the thread end (DIN 76-2 / ISO
  3508 thread relief; internal threads).

:func:`apply` is the single dispatch entry point used by
:mod:`geometry.builder`; it picks the right feature based on the
requested ``runout`` mode.
"""

from freecad.ThreadWorkbench.translations import translate

from .pocket import fill_pocket
from .tapered import build_tapered
from .undercut import build_undercut

__all__ = [
    "apply",
    "fill_pocket",
    "build_tapered",
    "build_undercut",
]


def apply(body, mode, *, far_end, back_dir, thread_end, origin, cut_dir, axis,
          pitch, main_helix_height, cyl_radius, is_external, diameter,
          profile, left_handed):
    """Apply a runout feature to the thread according to ``mode``.

    Supported modes:
        ``"none"``     — no extra feature (abrupt end; for milling/tapping).
        ``"pocket"``   — additive fill flush with the surface (external).
        ``"tapered"``  — conical helix fading the groove (external).
        ``"undercut"`` — subtractive relief groove past the thread end
                         (DIN 76-2 / ISO 3508; internal).

    Unknown modes are treated as ``"none"``.
    Raises :class:`RuntimeError` (already translated) if the underlying
    PartDesign operation fails.
    """
    if mode == "pocket":
        return fill_pocket(body, far_end, back_dir, pitch, cyl_radius,
                           is_external, diameter, profile)

    if mode == "tapered":
        try:
            return build_tapered(body, origin, cut_dir, axis, pitch,
                                 cyl_radius, main_helix_height, is_external,
                                 diameter, profile, left_handed)
        except Exception as e:
            raise RuntimeError(
                translate("err_runout_failed",
                          "Failed to create tapered runout: {e}")
                .format(e=e)) from e

    if mode == "undercut":
        try:
            return build_undercut(body, thread_end, cut_dir, pitch,
                                  cyl_radius, is_external, diameter, profile,
                                  length_factor=3.0)
        except Exception as e:
            raise RuntimeError(
                translate("err_undercut_failed",
                          "Failed to create undercut runout: {e}")
                .format(e=e)) from e

    if mode == "undercut_narrow":
        try:
            return build_undercut(body, thread_end, cut_dir, pitch,
                                  cyl_radius, is_external, diameter, profile,
                                  length_factor=2.0)
        except Exception as e:
            raise RuntimeError(
                translate("err_undercut_failed",
                          "Failed to create undercut runout: {e}")
                .format(e=e)) from e

    # "none" or anything else: do nothing.
    return None
