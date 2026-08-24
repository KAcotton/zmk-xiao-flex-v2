// TylerDactyl v0.1 modular baseplate — shared parameters.
//
// Footprint numbers below are RAW STL BOUNDING BOXES from the existing v1
// CASE/HOLDER/PLATE meshes (hardware/cad/*.stl), taken from each file's own
// local coordinate frame. They are reliable for in-file size/thickness, but
// the files are NOT confirmed to share a common assembly origin, so any
// cross-file stack-height inference is an assumption, not a measurement.
// See hardware/design-notes/v0.1-baseplate-tenting-battery.md for details.

// ---- Case footprints (X = medial/lateral width, Y = front/back depth), mm --
FOOT_L = [150.4, 147.3];
FOOT_R = [182.3, 157.8];

// Existing flat baseplate thickness (v1), for reference only.
PLATE_THK_V1 = 3.0;

// Existing PCB/board holder footprint — must stay clear above the new
// baseplate's top (case-mating) face; key/matrix + trackball geometry is
// unchanged and lives above this line.
HOLDER_FOOT = [82.5, 45.2];
HOLDER_HEIGHT = 8.5;

// nice!nano v2 controller board envelope: width x length x pcb thickness.
// Verify against the actual part before fabrication.
NICE_NANO = [18.0, 33.0, 1.6];
NICE_NANO_SOCKET_H = 8.5; // pin header / socket stack height, typical pro-micro-family

// 18650 cell (protected, flat-top) + generic single-cell wire-lead holder.
// ASSUMPTION: exact holder SKU not yet selected — dimensions below are a
// generous placeholder envelope. Confirm real part before fabrication.
CELL_DIA = 18.5;   // bare cell ~18.0-18.4mm; +wrap clearance
CELL_LEN = 70.0;   // protected flat-top cells commonly run 67-70mm
CELL_HOLDER_ENV = [CELL_DIA + 3, CELL_LEN + 6, 12]; // W x L x H incl. spring clips

// Printed-part nominal parameters.
WALL = 2.2;
FLOOR = 2.0;
CLR = 0.4;

// Corner mounting-post inset from the footprint edge.
// PLACEHOLDER — NOT derived from the real case screw-boss positions (those
// were not extracted from the STL in this pass). Must be verified/measured
// against the actual CASE bottom rim before any part is fabricated.
CORNER_INSET = [12, 12];

// Fastener sizing (generic M3).
M3_CLR_D = 3.4;
M3_HEAD_D = 6.0;
M3_HEAD_H = 2.4;
M3_BOSS_D = 6.0;

// New baseplate tray depth (below the case-mating top face), sized to clear
// the 18650 holder height and a socketed nice!nano v2.
TRAY_DEPTH = 16.0;

// Tenting shim baseline height (the "0 degree / low corner" standoff height).
SHIM_BASE_H = 6.0;

// Discrete tenting angle set (degrees) — see open questions before locking in.
TENT_ANGLES = [8, 12, 16, 20];

module __params_unit_test() {} // placeholder so this file is a valid, includable module scope
