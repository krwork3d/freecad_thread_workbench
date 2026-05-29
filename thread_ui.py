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

"""UI assembly for the Thread Workbench task panel."""

from PySide import QtWidgets

from translations import translate

_CUSTOM = translate("Custom", "— Custom —")


def _make_param_group(thread_mode, on_custom_changed, on_pitch_mm_changed):
    """Build the «Thread Parameters» QGroupBox.

    Returns (group_box, dict_of_widgets).

    Metric: combos + spinners, always visible, mutually synced.
    Inch:   spinners + preset (preset built in setup_ui).
    """
    is_inch = thread_mode == "inch"
    gb = QtWidgets.QGroupBox(translate("ParamGroup", "Thread Parameters"))
    gb_lay = QtWidgets.QVBoxLayout(gb)
    widgets = {}

    if is_inch:
        # Diameter in inches
        dia_lay = QtWidgets.QHBoxLayout()
        dia_lay.addWidget(QtWidgets.QLabel(
            translate("InchDiaLabel", "Nominal diameter (inch):")))
        spin_dia = QtWidgets.QDoubleSpinBox()
        spin_dia.setRange(0.01, 4.0)
        spin_dia.setValue(0.25)
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
        # ── Metric: combobox + spinner always visible ──
        from thread_presets import metric_diameters, metric_pitches_for

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

        def _on_dia_combo(_idx):
            txt = cb_diameter.currentText()
            if txt == _CUSTOM:
                return
            d = float(txt[1:])  # "M10" → 10.0
            spin_dia.setValue(d)
            _fill_pitches(cb_diameter, cb_pitch, spin_pitch)

        def _on_dia_spin(_val):
            d = spin_dia.value()
            for i, dia_val in enumerate(diameters):
                if abs(dia_val - d) < 0.001:
                    cb_diameter.setCurrentIndex(i)
                    return
            cb_diameter.setCurrentIndex(cb_diameter.count() - 1)
            _fill_pitches(cb_diameter, cb_pitch, spin_pitch)

        cb_diameter.currentIndexChanged.connect(_on_dia_combo)
        spin_dia.valueChanged.connect(_on_dia_spin)
        dia_lay.addWidget(cb_diameter)
        dia_lay.addWidget(spin_dia)
        gb_lay.addLayout(dia_lay)

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

        def _fill_pitches(diameter_cb, pitch_cb, pitch_spin):
            if diameter_cb.currentText() == _CUSTOM:
                pitch_cb.clear()
                pitch_cb.addItem(_CUSTOM, -1.0)
                pitch_cb.setCurrentIndex(0)
                return
            txt = diameter_cb.currentText()
            d = float(txt[1:])  # "M10" → 10.0
            pitches = metric_pitches_for(d)
            pitch_cb.clear()
            for p, _name in pitches:
                pitch_cb.addItem(f"{p:g}", p)
            pitch_cb.addItem(_CUSTOM, -1.0)
            if pitches:
                first_p = pitches[0][0]
                pitch_cb.setCurrentIndex(0)
                pitch_spin.setValue(first_p)

        def _on_pitch_combo(_txt):
            data = cb_pitch.currentData()
            if data is not None and data > 0:
                spin_pitch.setValue(data)

        def _on_pitch_spin(_val):
            p = spin_pitch.value()
            for i in range(cb_pitch.count()):
                d = cb_pitch.itemData(i)
                if d is not None and d > 0 and abs(d - p) < 0.001:
                    cb_pitch.setCurrentIndex(i)
                    return
            cb_pitch.setCurrentIndex(cb_pitch.count() - 1)

        _fill_pitches(cb_diameter, cb_pitch, spin_pitch)
        cb_pitch.currentTextChanged.connect(_on_pitch_combo)
        spin_pitch.valueChanged.connect(_on_pitch_spin)
        pitch_lay.addWidget(cb_pitch)
        pitch_lay.addWidget(spin_pitch)
        gb_lay.addLayout(pitch_lay)

        widgets.update(
            cb_diameter=cb_diameter, spin_dia=spin_dia,
            cb_pitch=cb_pitch, spin_pitch=spin_pitch,
            _fill_pitches=_fill_pitches,
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

    widgets.update(spin_len=spin_len, spin_off=spin_off,
                   cb_start_edge=cb_start_edge)

    return gb, widgets


def _make_directions_group():
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


def setup_ui(thread_mode, on_preset, on_custom, on_edge_to_edge,
             on_create, on_pitch_mm_changed):
    """Build and return (root_widget, widgets).

    widgets — flat dict of all significant controls.

    Metric: combos + spinners for diameter/pitch (no flat preset).
    Inch:   spinners + flat preset cb_preset.
    """
    form = QtWidgets.QWidget()
    form.setMinimumWidth(400)
    layout = QtWidgets.QVBoxLayout(form)
    is_inch = thread_mode == "inch"

    # ── Preset (inch only) ──
    if is_inch:
        from thread_presets import inch_presets
        presets = inch_presets()
        pres_layout = QtWidgets.QHBoxLayout()
        pres_layout.addWidget(QtWidgets.QLabel(
            translate("PresetLabel", "Preset:")))
        cb_preset = QtWidgets.QComboBox()
        cb_preset.addItem(_CUSTOM)
        for name in presets:
            cb_preset.addItem(name)
        cb_preset.currentTextChanged.connect(on_preset)
        pres_layout.addWidget(cb_preset)
        layout.addLayout(pres_layout)
    else:
        cb_preset = None

    # ── Thread Parameters ──
    param_gb, param_w = _make_param_group(
        thread_mode, on_custom, on_pitch_mm_changed,
    )
    layout.addWidget(param_gb)

    # ── Type ──
    type_lay = QtWidgets.QHBoxLayout()
    type_lay.addWidget(QtWidgets.QLabel(translate("TypeLabel", "Type:")))
    cb_type = QtWidgets.QComboBox()
    cb_type.addItem(translate("External", "External"))
    cb_type.addItem(translate("Internal", "Internal"))
    type_lay.addWidget(cb_type)
    layout.addLayout(type_lay)

    # ── Direction ──
    dir_gb, dir_w = _make_directions_group()
    layout.addWidget(dir_gb)

    # ── Live Preview ──
    chk_preview = QtWidgets.QCheckBox(
        translate("LivePreview", "Live preview"))
    chk_preview.setChecked(False)
    layout.addWidget(chk_preview)

    # ── Auto-length ──
    chk_e2e = QtWidgets.QCheckBox(
        translate("EdgeToEdge", "Edge-to-edge (entire face)"))
    chk_e2e.setChecked(False)
    chk_e2e.toggled.connect(on_edge_to_edge)
    layout.addWidget(chk_e2e)

    # ── Runout ──
    chk_runout = QtWidgets.QCheckBox(
        translate("Runout", "Smooth runout (additive)"))
    chk_runout.setChecked(True)
    chk_runout.setToolTip(translate("RunoutTip",
                                    "Add a conical fill at the far end to close "
                                    "the groove smoothly, like Fusion 360"))
    layout.addWidget(chk_runout)

    # ── «Create» button ──
    btn_go = QtWidgets.QPushButton(
        translate("CreateButton", "Create Thread"))
    btn_go.clicked.connect(on_create)
    btn_go.setMinimumHeight(36)
    layout.addWidget(btn_go)

    # ── Status ──
    lbl_status = QtWidgets.QLabel(
        translate("StatusDefault",
                  "Select a cylindrical face on an object inside "
                  "a PartDesign::Body"))
    lbl_status.setWordWrap(True)
    layout.addWidget(lbl_status)

    layout.addStretch()

    # ── Collect all widgets ──
    widgets = dict(
        cb_type=cb_type,
        chk_e2e=chk_e2e,
        chk_preview=chk_preview,
        chk_runout=chk_runout,
        btn_go=btn_go,
        lbl_status=lbl_status,
    )
    if cb_preset is not None:
        widgets["cb_preset"] = cb_preset
    widgets.update(param_w)
    widgets.update(dir_w)

    return form, widgets
