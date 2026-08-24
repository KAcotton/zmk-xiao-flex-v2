// TylerDactyl v0.2 — visual fit-check overlay (RIGHT).
// Preview only (F5) — see fit_check_left.scad header note.

include <lib/params_v2.scad>
include <lib/organic_outline.scad>
include <lib/organic_tray.scad>

case_solid_preview("right");
plate_solid_preview("right");

BATTERY_POS = [-90, -70, TRAY_DEPTH / 2];
CONTROLLER_POS = [40, 25];
organic_tray("right", BATTERY_POS, CONTROLLER_POS);
