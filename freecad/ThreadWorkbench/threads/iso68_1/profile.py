# -*- coding: utf-8 -*-
"""Thread profile per ISO 68-1 standard (metric threads).

Truncated trapezoid with a flat root (root flat = P/4).

Used for ISO 261/262/724 metric threads.
"""

from freecad.ThreadWorkbench.threads.base import AbstractThreadProfile, _register


@_register
class ISO68_1Profile(AbstractThreadProfile):
    """ISO 68-1 — metric profile with a flat root.

    Geometry (external thread, subtractive groove profile):
       Y=0      P/16      3P/8     5P/8    15P/16    P
        |  crest |         |         |         | crest |
    r   |________|         |         |         |_______|
        |        \\        |         |        //       |
        |         \\       |         |       //        |
        |          \\      |_________|      //         |
        |           |   root flat  |              |
    r-h |           |____P/4_____|              |

    h = 5/8 H = (5√3/16) × P  — working depth

    Crest flat = H/8 off the tip  → width P/8
    Root flat  = H/4 off the base → width P/4
    """

    PROFILE_ID = "iso68_1"
    LABEL = "ISO 68-1 (Metric)"

    def build_profile(self, pitch, cyl_radius, is_external):
        h_work = self._working_depth(pitch)
        r_surface, r_root = self._surface_radii(cyl_radius, h_work, is_external)
        return self._make_flat_root_points(pitch, r_surface, r_root)
