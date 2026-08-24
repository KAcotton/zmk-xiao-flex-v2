// TylerDactyl v0.2 — visual fit-check overlay (LEFT).
// Preview only (F5) — do NOT F6/CGAL-render this file: the CASE mesh is
// non-manifold and %import() preview overlays are fine, but this file
// mixes real solids (the new tray) with translucent reference imports
// purely so a human can eyeball alignment. Not exportable geometry.

include <lib/params_v2.scad>
include <lib/organic_outline.scad>
include <lib/organic_tray.scad>

case_solid_preview("left");
plate_solid_preview("left");

BATTERY_POS = [-10, -70, TRAY_DEPTH / 2];
CONTROLLER_POS = [60, 30];
organic_tray("left", BATTERY_POS, CONTROLLER_POS);
