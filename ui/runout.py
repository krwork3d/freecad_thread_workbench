# -*- coding: utf-8 -*-


"""Runout availability rules mixin for ThreadTaskPanel."""


class RunoutMixin:
    """Provides runout availability logic based on thread type."""

    # data → (allowed_for_external, allowed_for_internal)
    _RUNOUT_RULES = {
        "none":           (True,  True),
        "pocket":         (True,  False),
        "tapered":        (True,  False),
        "undercut":       (False, True),
        "undercut_narrow":(False, True),
    }

    def _on_type_changed(self, idx):
        """Enable only runout modes that are sensible for the chosen type.

        External: pocket / tapered / none.
        Internal: undercut / none (DIN 76-2 thread relief).
        """
        is_external = (idx == 0)
        cb = self._widgets["cb_runout"]
        model = cb.model()

        for i in range(cb.count()):
            data = cb.itemData(i)
            ext_ok, int_ok = self._RUNOUT_RULES.get(data, (True, True))
            allowed = ext_ok if is_external else int_ok
            item = model.item(i)
            if item is not None:
                item.setEnabled(allowed)

        # If current selection is now disabled, switch to a sensible default.
        cur_data = cb.currentData()
        cur_ext, cur_int = self._RUNOUT_RULES.get(cur_data, (True, True))
        if (is_external and not cur_ext) or (not is_external and not cur_int):
            default_data = "pocket" if is_external else "undercut"
            for i in range(cb.count()):
                if cb.itemData(i) == default_data:
                    cb.setCurrentIndex(i)
                    break
