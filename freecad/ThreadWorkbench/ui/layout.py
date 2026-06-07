# -*- coding: utf-8 -*-

"""Layout assembly for the Thread Workbench task panel form."""

from PySide import QtWidgets

from freecad.ThreadWorkbench.translations import translate
from freecad.ThreadWorkbench.ui.widgets import make_param_group, make_directions_group, make_runout_combo

_CUSTOM = translate("Custom", "— Custom —")


def build_form(thread_mode, on_preset, on_custom, on_edge_to_edge,
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
        from freecad.ThreadWorkbench.thread_presets import inch_presets
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
    param_gb, param_w = make_param_group(
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
    dir_gb, dir_w = make_directions_group()
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
    runout_lay = QtWidgets.QHBoxLayout()
    runout_lay.addWidget(QtWidgets.QLabel(
        translate("RunoutLabel", "Runout:")))
    cb_runout = make_runout_combo()
    runout_lay.addWidget(cb_runout)
    layout.addLayout(runout_lay)

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
        cb_runout=cb_runout,
        btn_go=btn_go,
        lbl_status=lbl_status,
    )
    if cb_preset is not None:
        widgets["cb_preset"] = cb_preset
    widgets.update(param_w)
    widgets.update(dir_w)

    return form, widgets
