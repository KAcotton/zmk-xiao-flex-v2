// TylerDactyl v0.2 modular baseplate — RIGHT half.
// Render/inspect: openscad hardware/cad/v0.2/baseplate_right.scad
// Export STL:     openscad -o baseplate_right.stl hardware/cad/v0.2/baseplate_right.scad
//
// Uses the REAL RIGHT CASE footprint (projection() of the actual mesh) as
// the tray's plan-view outline. Battery/controller placement is pushed
// away from the approximate center of the case (where the photo shows the
// trackball sits) — this is a visual guess, NOT a measured trackball
// keepout. See design notes open questions before trusting this.

include <lib/params_v2.scad>
include <lib/organic_outline.scad>
include <lib/organic_tray.scad>

// PLACEHOLDER positions — see baseplate_left.scad header note.
BATTERY_POS = [-90, -70, TRAY_DEPTH / 2];
CONTROLLER_POS = [40, 25];

organic_tray("right", BATTERY_POS, CONTROLLER_POS);
