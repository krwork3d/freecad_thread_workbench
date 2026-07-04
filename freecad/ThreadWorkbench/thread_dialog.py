# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Thread Workbench for FreeCAD                                          *
# *   Copyright (c) 2025                                                    *
# *                                                                         *
# *   This program is free software: you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation, either version 3 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU General Public License for more details.                          *
# *                                                                         *
# *   You should have received a copy of the GNU General Public License     *
# *   along with this program.  If not, see <http://www.gnu.org/licenses/>. *
# ***************************************************************************

"""Task panel for thread creation — thin orchestrator.

All UI logic is delegated to mixins in the ``ui`` package:
  - PreviewMixin      — live Coin3D preview
  - ScanningMixin     — face scanning and edge detection
  - CreationMixin     — thread feature creation
  - PresetsMixin      — preset selection and custom parameters
  - RunoutMixin       — runout availability rules
  - SelectionMixin    — auto-tracking selection changes
"""

import FreeCADGui as Gui
from PySide import QtWidgets, QtCore

from freecad.ThreadWorkbench.geometry import FaceAnalysis, ThreadPreview
from freecad.ThreadWorkbench.thread_presets import profile_id_for_type
from freecad.ThreadWorkbench.ui import (
    setup_ui,
    PreviewMixin,
    ScanningMixin,
    CreationMixin,
    PresetsMixin,
    RunoutMixin,
    SelectionMixin,
)


class ThreadTaskPanel(
    PreviewMixin,
    ScanningMixin,
    CreationMixin,
    PresetsMixin,
    RunoutMixin,
    SelectionMixin,
):
    """Task panel: select a face, set parameters, and build a thread.

    Non-blocking — the user can freely switch selection.

    Parameters
    ----------
    thread_mode : "metric" | "inch"
    """

    def __init__(self, thread_mode="metric"):
        self._thread_mode = thread_mode
        self._profile_id = profile_id_for_type(thread_mode)

        self._updating_ui = False
        self._analysis = FaceAnalysis()
        self._first_scan = True
        self._last_selection_key = None
        self._widgets = {}
        self._preview = ThreadPreview()

        self._setup_ui()
        self.scan_selection()

        # Timer to poll selection changes
        self._poll_timer = QtCore.QTimer()
        self._poll_timer.setInterval(400)
        self._poll_timer.timeout.connect(self._poll_selection)
        self._poll_timer.start()

    # ═════════════════════════════════════════════════════════════
    # Task Panel protocol
    # ═════════════════════════════════════════════════════════════

    def getStandardButtons(self):
        return int(QtWidgets.QDialogButtonBox.StandardButton.Close.value)

    def clicked(self, bt):
        if bt == QtWidgets.QDialogButtonBox.Close:
            self.finish()

    def accept(self):
        self.finish()

    def reject(self):
        self.finish()

    def finish(self):
        self._poll_timer.stop()
        self._preview.remove()
        Gui.Control.closeDialog()

    # ═════════════════════════════════════════════════════════════
    # UI setup
    # ═════════════════════════════════════════════════════════════

    def _setup_ui(self):
        self.form, self._widgets = setup_ui(
            thread_mode=self._thread_mode,
            on_preset=self._on_preset,
            on_custom=self._on_custom,
            on_edge_to_edge=self._on_edge_to_edge,
            on_create=self._run,
            on_pitch_mm_changed=self._update_pitch_mm_label,
        )

        w = self._widgets
        w["chk_preview"].toggled.connect(self._on_preview_toggled)

        # Connect ALL parameter changes to preview update
        if self._thread_mode == "metric":
            w["cb_diameter"].currentIndexChanged.connect(self._schedule_preview)
            w["spin_dia"].valueChanged.connect(self._schedule_preview)
            w["cb_pitch"].currentTextChanged.connect(self._schedule_preview)
            w["spin_pitch"].valueChanged.connect(self._schedule_preview)
        else:  # inch, bsp — TPI-based
            w["spin_dia"].valueChanged.connect(self._schedule_preview)
            w["spin_tpi"].valueChanged.connect(self._schedule_preview)
            w["spin_tpi"].valueChanged.connect(self._update_pitch_mm_label)

        w["spin_len"].valueChanged.connect(self._schedule_preview)
        w["spin_off"].valueChanged.connect(self._schedule_preview)
        w["spin_clearance"].valueChanged.connect(self._schedule_preview)
        w["cb_type"].currentIndexChanged.connect(self._schedule_preview)
        w["cb_type"].currentIndexChanged.connect(self._on_type_changed)
        w["chk_reversed"].toggled.connect(self._schedule_preview)
        w["chk_left"].toggled.connect(self._schedule_preview)
        w["chk_e2e"].toggled.connect(self._schedule_preview)
        w["cb_runout"].currentIndexChanged.connect(self._schedule_preview)
        w["cb_start_edge"].currentIndexChanged.connect(self._schedule_preview)

        self._on_type_changed(w["cb_type"].currentIndex())

        # Debounce timer
        self._preview_timer = QtCore.QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(200)
        self._preview_timer.timeout.connect(self._do_preview)

