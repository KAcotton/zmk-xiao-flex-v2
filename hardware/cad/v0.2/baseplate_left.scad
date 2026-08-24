// TylerDactyl v0.2 modular baseplate — LEFT half.
// Render/inspect: openscad hardware/cad/v0.2/baseplate_left.scad
// Export STL:     openscad -o baseplate_left.stl hardware/cad/v0.2/baseplate_left.scad
//
// Uses the REAL LEFT CASE footprint (projection() of the actual mesh, see
// lib/organic_outline.scad) as the tray's plan-view outline instead of a
// bounding-box rectangle. See hardware/design-notes/
// v0.2-baseplate-tenting-battery.md for what this does and does not solve.

include <lib/params_v2.scad>
include <lib/organic_outline.scad>
include <lib/organic_tray.scad>

// PLACEHOLDER positions — not verified against real local wall thickness
// or against real screw/keepout locations. Open the render and check
// visually before trusting these.
BATTERY_POS = [-10, -70, TRAY_DEPTH / 2];
CONTROLLER_POS = [60, 30];

organic_tray("left", BATTERY_POS, CONTROLLER_POS);
