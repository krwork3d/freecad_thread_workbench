# -*- coding: utf-8 -*-
"""Thread geometry calculations.

Public API (re-exported here for convenience):

* :class:`FaceAnalysis`  — analyse a selected cylindrical face.
* :func:`create_thread`  — build the full thread feature inside a Body.
* :class:`ThreadPreview` — Coin3D overlay for live parameter preview.
* :func:`build_local_frame` — sketch orientation helper.

The package is split into small logical modules:

* :mod:`geometry.frame`         — local sketch frame helper.
* :mod:`geometry.face_analysis` — selection / face inspection.
* :mod:`geometry.helix`         — helix feature primitive.
* :mod:`geometry.precut`        — pre-cut cylindrical Groove.
* :mod:`geometry.builder`       — main ``create_thread`` orchestrator.
* :mod:`geometry.runout`        — runout / end-of-thread features.
* :mod:`geometry.preview`       — Coin3D preview overlay.
"""

from .frame import build_local_frame
from .face_analysis import FaceAnalysis
from .builder import create_thread
from .preview import ThreadPreview
from .thread_frame import resolve_thread_frame

__all__ = [
    "build_local_frame",
    "FaceAnalysis",
    "create_thread",
    "ThreadPreview",
    "resolve_thread_frame",
]
