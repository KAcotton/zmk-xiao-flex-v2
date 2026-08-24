// TylerDactyl v0.1 modular baseplate — LEFT half.
// Render/inspect: openscad hardware/cad/v0.1/baseplate_left.scad
// Export STL:     openscad -o baseplate_left.stl hardware/cad/v0.1/baseplate_left.scad
//
// NOT YET RENDERED OR VALIDATED — no OpenSCAD install was available in this
// pass. Syntax and geometry are authored carefully but must be opened and
// inspected in OpenSCAD (or FreeCAD/Fusion via import) before printing.

include <lib/params.scad>
include <lib/baseplate_tray.scad>

baseplate_tray(
    footprint = FOOT_L,
    corner_inset = CORNER_INSET,
    battery_edge = "back",
    controller_corner = [1, -1] // front-right corner of the left half
);
