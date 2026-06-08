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

"""UI handlers and synchronisation logic for metric diameter/pitch combos."""

from freecad.ThreadWorkbench.translations import translate

_CUSTOM = translate("Custom", "— Custom —")


def make_metric_diameter_handlers(cb_diameter, spin_dia, cb_pitch, spin_pitch, diameters):
    """Return (on_dia_combo, on_dia_spin, fill_pitches, on_pitch_combo, on_pitch_spin).

    These closures keep the metric diameter/pitch combo-boxes and spinners in sync.
    """
    from freecad.ThreadWorkbench.thread_presets import metric_pitches_for

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

    return _on_dia_combo, _on_dia_spin, _fill_pitches, _on_pitch_combo, _on_pitch_spin
