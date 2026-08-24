// TylerDactyl v0.1 modular baseplate — visual fit-check overlay (RIGHT).
// See fit_check_left.scad header for caveats. Preview only, do not export.

include <lib/params.scad>
include <lib/baseplate_tray.scad>

%import("../21.05.02 CASE RIGHT.stl");
%import("../21.05.06 PLATE RIGHT.stl");

color("steelblue", 0.6)
    baseplate_tray(
        footprint = FOOT_R,
        corner_inset = CORNER_INSET,
        battery_edge = "back",
        controller_corner = [-1, -1],
        keepout = [[40, 40, TRAY_DEPTH], [FOOT_R[0] / 2 - 30, FOOT_R[1] / 2 - 30]]
    );
