// TylerDactyl v0.1 modular baseplate — RIGHT half.
// Render/inspect: openscad hardware/cad/v0.1/baseplate_right.scad
// Export STL:     openscad -o baseplate_right.stl hardware/cad/v0.1/baseplate_right.scad
//
// NOT YET RENDERED OR VALIDATED — no OpenSCAD install was available in this
// pass. Syntax and geometry are authored carefully but must be opened and
// inspected in OpenSCAD (or FreeCAD/Fusion via import) before printing.
//
// The translucent (%) keepout box below is a PLACEHOLDER for the PMW3610
// trackball/encoder clearance envelope. Its position was NOT derived from
// the CASE RIGHT / HOLDER RIGHT mesh in this pass — it is a rough guess at
// the back-right corner and MUST be replaced with a real measurement before
// the controller/battery layout is trusted for this half.

include <lib/params.scad>
include <lib/baseplate_tray.scad>

baseplate_tray(
    footprint = FOOT_R,
    corner_inset = CORNER_INSET,
    battery_edge = "back",
    controller_corner = [-1, -1], // front-left corner, away from trackball guess-zone
    keepout = [[40, 40, TRAY_DEPTH], [FOOT_R[0] / 2 - 30, FOOT_R[1] / 2 - 30]]
);
