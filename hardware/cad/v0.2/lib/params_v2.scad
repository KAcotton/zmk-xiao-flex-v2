// TylerDactyl v0.2 modular baseplate — shared parameters.
//
// Numbers here are MEASURED (numpy-stl) from the real reference meshes in
// hardware/cad/, not guessed. See hardware/design-notes/
// v0.2-baseplate-tenting-battery.md for the full measurement log.

// ---- Confirmed-shared-frame footprint bounding boxes (X, Y), mm ----------
// CASE and PLATE share the same X/Y origin per half (bboxes matched exactly
// when measured independently); Z origin between files is still NOT
// confirmed shared — do not trust cross-file Z stack-up numbers.
FOOT_L = [150.4, 147.3]; // CASE LEFT / PLATE LEFT bbox X x Y
FOOT_R = [182.3, 157.8]; // CASE RIGHT / PLATE RIGHT bbox X x Y

// The outlines are NOT centered on the origin — use these real min/max
// corners (not footprint/2) for any XY placement math.
FOOT_L_MIN = [-65.39057, -100.06601];
FOOT_L_MAX = [84.98351, 47.187004];
FOOT_R_MIN = [-116.903076, -110.61613];
FOOT_R_MAX = [65.39057, 47.187004];

// CASE mesh Z extents (each file's own frame) — for reference only.
CASE_L_ZMIN = 3.0;
CASE_L_ZMAX = 70.387146;
CASE_R_ZMIN = 3.0;
CASE_R_ZMAX = 65.50965;

// PLATE thickness — measured uniform ~3.0mm flat sheet (both halves).
PLATE_THK = 3.0;

// Existing PCB/board holder footprint (unchanged reference geometry).
HOLDER_FOOT = [82.5, 45.2];
HOLDER_HEIGHT = 8.5;

// nice!nano v2 controller board envelope: width x length x pcb thickness.
NICE_NANO = [18.0, 33.0, 1.6];

// 18650 cell: 18mm dia x 65mm length (per corrected spec), plus fit
// clearance and JST connector/lead length allowance.
CELL_DIA = 18.0;
CELL_LEN = 65.0;
CELL_FIT_CLR = 0.6;   // radial clearance so a real cell/holder slides in
JST_CLR_LEN = 12.0;   // extra pocket length for JST plug + strain relief
POCKET_DIA = CELL_DIA + 2 * CELL_FIT_CLR;
POCKET_LEN = CELL_LEN + JST_CLR_LEN;

// Printed-part nominal parameters.
WALL = 2.2;
FLOOR = 2.0;
CLR = 0.4;

// Tray depth: must clear the battery pocket diameter plus floor/roof margin.
TRAY_DEPTH = POCKET_DIA + FLOOR + 4.0; // ~24.8mm

// Fastener sizing (generic M3).
M3_CLR_D = 3.4;
M3_HEAD_D = 6.0;
M3_HEAD_H = 2.4;
M3_BOSS_D = 6.0;

// Corner mounting-post inset from the case footprint's bounding-box edge.
// STILL A PLACEHOLDER — real CASE screw-boss positions were not extracted
// from the mesh in this pass either (same open item carried over from
// v0.1). Because the footprint is an organic outline, not a rectangle, a
// post at this inset may land over empty space (a cutout) rather than
// solid wall — visually verify in the OpenSCAD preview before trusting it.
CORNER_INSET = [12, 12];

module __params_v2_unit_test() {}
