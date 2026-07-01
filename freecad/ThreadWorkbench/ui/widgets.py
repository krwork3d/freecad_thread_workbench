# -*- coding: utf-8 -*-


"""Reusable widget builders for the Thread Workbench task panel."""

from PySide import QtWidgets

from freecad.ThreadWorkbench.translations import translate
from freecad.ThreadWorkbench.ui.handlers import make_metric_diameter_handlers

_CUSTOM = translate("Custom", "— Custom —")


def make_param_group(thread_mode, on_custom_changed, on_pitch_mm_changed):
    """Build the «Thread Parameters» QGroupBox.

    Returns (group_box, dict_of_widgets).

    Metric: combos + spinners, always visible, mutually synced.
    Inch/BSP: spinners + preset (preset built in setup_ui).
    """
    is_tpi = thread_mode in ("inch", "bsp")
    gb = QtWidgets.QGroupBox(translate("ParamGroup", "Thread Parameters"))
    gb_lay = QtWidgets.QVBoxLayout(gb)
    widgets = {}

    if is_tpi:
        # Diameter in inches
        max_dia = 8.0 if thread_mode == "bsp" else 4.0
        default_dia = 0.825 if thread_mode == "bsp" else 0.25
        dia_lay = QtWidgets.QHBoxLayout()
        dia_lay.addWidget(QtWidgets.QLabel(
            translate("InchDiaLabel", "Nominal diameter (inch):")))
        spin_dia = QtWidgets.QDoubleSpinBox()
        spin_dia.setRange(0.01, max_dia)
        spin_dia.setValue(default_dia)
        spin_dia.setDecimals(4)
        spin_dia.setSingleStep(0.0625)
        spin_dia.valueChanged.connect(on_custom_changed)
        dia_lay.addWidget(spin_dia)
        gb_lay.addLayout(dia_lay)

        # TPI
        tpi_lay = QtWidgets.QHBoxLayout()
        tpi_lay.addWidget(QtWidgets.QLabel(
            translate("InchTPILabel", "TPI (threads/inch):")))
        spin_tpi = QtWidgets.QSpinBox()
        spin_tpi.setRange(1, 80)
        spin_tpi.setValue(20)
        spin_tpi.valueChanged.connect(on_custom_changed)
        spin_tpi.valueChanged.connect(on_pitch_mm_changed)
        tpi_lay.addWidget(spin_tpi)
        gb_lay.addLayout(tpi_lay)

        # Computed pitch in mm (read-only)
        pitch_mm_lay = QtWidgets.QHBoxLayout()
        pitch_mm_lay.addWidget(QtWidgets.QLabel(
            translate("PitchMmLabel", "Pitch (mm, computed):")))
        lbl_pitch_mm = QtWidgets.QLabel("1.27")
        pitch_mm_lay.addWidget(lbl_pitch_mm)
        pitch_mm_lay.addStretch()
        gb_lay.addLayout(pitch_mm_lay)

        widgets.update(spin_dia=spin_dia, spin_tpi=spin_tpi,
                       lbl_pitch_mm=lbl_pitch_mm)
    else:
        from freecad.ThreadWorkbench.thread_presets import metric_diameters

        diameters = metric_diameters()

        # -- Diameter --
        dia_lay = QtWidgets.QHBoxLayout()
        dia_lay.addWidget(QtWidgets.QLabel(
            translate("DiameterLabel", "Diameter:")))
        cb_diameter = QtWidgets.QComboBox()
        cb_diameter.addItems([f"M{d:g}" for d in diameters])
        cb_diameter.addItem(_CUSTOM)
        cb_diameter.setCurrentIndex(diameters.index(10.0))

        spin_dia = QtWidgets.QDoubleSpinBox()
        spin_dia.setRange(0.5, 500.0)
        spin_dia.setValue(10.0)
        spin_dia.setDecimals(2)
        spin_dia.setSingleStep(1.0)

        # -- Pitch --
        pitch_lay = QtWidgets.QHBoxLayout()
        pitch_lay.addWidget(QtWidgets.QLabel(
            translate("PitchLabel", "Pitch (mm):")))
        cb_pitch = QtWidgets.QComboBox()

        spin_pitch = QtWidgets.QDoubleSpinBox()
        spin_pitch.setRange(0.1, 50.0)
        spin_pitch.setValue(1.5)
        spin_pitch.setDecimals(3)
        spin_pitch.setSingleStep(0.25)

        # Wire up metric handlers
        on_dia_combo, on_dia_spin, fill_pitches, on_pitch_combo, on_pitch_spin = \
            make_metric_diameter_handlers(cb_diameter, spin_dia, cb_pitch, spin_pitch, diameters)

        cb_diameter.currentIndexChanged.connect(on_dia_combo)
        spin_dia.valueChanged.connect(on_dia_spin)
        fill_pitches(cb_diameter, cb_pitch, spin_pitch)
        cb_pitch.currentTextChanged.connect(on_pitch_combo)
        spin_pitch.valueChanged.connect(on_pitch_spin)

        dia_lay.addWidget(cb_diameter)
        dia_lay.addWidget(spin_dia)
        gb_lay.addLayout(dia_lay)

        pitch_lay.addWidget(cb_pitch)
        pitch_lay.addWidget(spin_pitch)
        gb_lay.addLayout(pitch_lay)

        widgets.update(
            cb_diameter=cb_diameter, spin_dia=spin_dia,
            cb_pitch=cb_pitch, spin_pitch=spin_pitch,
        )

    # Common fields (length, offset)
    len_lay = QtWidgets.QHBoxLayout()
    len_lay.addWidget(QtWidgets.QLabel(
        translate("LengthLabel", "Thread length (mm):")))
    spin_len = QtWidgets.QDoubleSpinBox()
    spin_len.setRange(1.0, 1000.0)
    spin_len.setValue(20.0)
    spin_len.setDecimals(2)
    len_lay.addWidget(spin_len)
    gb_lay.addLayout(len_lay)

    off_lay = QtWidgets.QHBoxLayout()
    off_lay.addWidget(QtWidgets.QLabel(
        translate("OffsetLabel", "Offset from edge (mm):")))
    spin_off = QtWidgets.QDoubleSpinBox()
    spin_off.setRange(-200.0, 200.0)
    spin_off.setValue(0.0)
    spin_off.setDecimals(2)
    off_lay.addWidget(spin_off)
    gb_lay.addLayout(off_lay)

    # Start edge selector
    edge_lay = QtWidgets.QHBoxLayout()
    edge_lay.addWidget(QtWidgets.QLabel(
        translate("StartEdgeLabel", "Start from edge:")))
    cb_start_edge = QtWidgets.QComboBox()
    cb_start_edge.addItem(translate("NoEdge", "— select a face first —"))
    cb_start_edge.setEnabled(False)
    edge_lay.addWidget(cb_start_edge)
    gb_lay.addLayout(edge_lay)

    # Clearance (radial overlap with stock surface)
    clr_lay = QtWidgets.QHBoxLayout()
    clr_lay.addWidget(QtWidgets.QLabel(
        translate("ClearanceLabel", "Clearance (mm):")))
    spin_clearance = QtWidgets.QDoubleSpinBox()
    spin_clearance.setRange(0.0, 5.0)
    spin_clearance.setValue(0.05)
    spin_clearance.setDecimals(3)
    spin_clearance.setSingleStep(0.01)
    spin_clearance.setToolTip(translate(
        "ClearanceTip",
        "Radial overlap of the cutting profile with the stock surface.\n"
        "Increase to cut deeper when stock is oversized (shaft > D)\n"
        "or undersized (bore < D). Default: 0.05 mm."))
    clr_lay.addWidget(spin_clearance)
    gb_lay.addLayout(clr_lay)

    widgets.update(spin_len=spin_len, spin_off=spin_off,
                   cb_start_edge=cb_start_edge,
                   spin_clearance=spin_clearance)

    return gb, widgets


def make_directions_group():
    """QGroupBox: «Direction» (Reversed + LeftHanded)."""
    gb = QtWidgets.QGroupBox(translate("DirectionGroup", "Direction"))
    lay = QtWidgets.QVBoxLayout(gb)

    chk_reversed = QtWidgets.QCheckBox(
        translate("Reversed", "Reversed direction"))
    chk_reversed.setChecked(False)
    lay.addWidget(chk_reversed)

    chk_left = QtWidgets.QCheckBox(
        translate("LeftHanded", "Left-handed thread"))
    chk_left.setChecked(False)
    lay.addWidget(chk_left)

    return gb, dict(chk_reversed=chk_reversed, chk_left=chk_left)


def make_runout_combo():
    """Create the runout combo box with all options and tooltips."""
    cb_runout = QtWidgets.QComboBox()
    cb_runout.addItem(translate("RunoutNone", "None"), "none")
    cb_runout.addItem(translate("RunoutPocket", "Fill (additive)"), "pocket")
    cb_runout.addItem(translate("RunoutTapered", "Tapered (smooth fade)"), "tapered")
    cb_runout.addItem(translate("RunoutUndercut", "Undercut (relief groove)"), "undercut")
    cb_runout.addItem(translate("RunoutUndercutNarrow", "Undercut narrow (form B)"), "undercut_narrow")
    cb_runout.setCurrentIndex(1)  # default: pocket
    cb_runout.setToolTip(translate("RunoutTip",
                                    "How the thread groove ends:\n"
                                    "- None: abrupt stop (milling, tap/die)\n"
                                    "- Pocket: additive fill (external)\n"
                                    "- Tapered: smooth fade over half a turn (external, real screw runout)\n"
                                    "- Undercut: relief groove 3·P (internal, DIN 76-2 form A)\n"
                                    "- Undercut narrow: relief groove 2·P (internal, DIN 76-2 form B)"))
    return cb_runout
