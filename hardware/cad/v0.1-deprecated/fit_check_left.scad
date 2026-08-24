// TylerDactyl v0.1 modular baseplate — visual fit-check overlay (LEFT).
//
// Loads the REAL existing v1 CASE + PLATE meshes translucently alongside the
// new baseplate tray footprint outline, purely so a human can sanity-check
// in-plane (X/Y) footprint alignment in the OpenSCAD preview. This does NOT
// validate Z stack-up / clearances — the existing STL files are exported
// independently and are not confirmed to share a common assembly origin
// (see hardware/design-notes/v0.1-baseplate-tenting-battery.md).
//
// Run with `openscad hardware/cad/v0.1/fit_check_left.scad` (preview only,
// do not export this file to STL).

include <lib/params.scad>
include <lib/baseplate_tray.scad>

%import("../21.05.01 CASE LEFT.stl");
%import("../21.05.04 PLATE LEFT.stl");

color("steelblue", 0.6)
    baseplate_tray(footprint = FOOT_L, corner_inset = CORNER_INSET,
                   battery_edge = "back", controller_corner = [1, -1]);
