// TylerDactyl v0.1 modular baseplate — interchangeable tenting shims.
//
// Mechanism: each half's tray (baseplate_left/right.scad) has a flat,
// horizontal top rim with 4 corner mounting posts, identical for every
// tenting angle. To tent the keyboard, print ONE matched set of 4 small
// corner blocks — 2 "low" (front + back, same lateral side) and 2 "high"
// (front + back, opposite side) — and sandwich them between the tray rim
// and the existing (unmodified) CASE bottom rim, through-bolted together.
// Changing the tenting angle = reprinting just these 4 small blocks, not
// the tray or the case.
//
// Tenting rotates about the front-back (Y) axis only (lateral roll) — this
// is a single-axis wedge; front/back pitch is not addressed in v0.1.
//
// NOT YET RENDERED OR VALIDATED — see baseplate_left.scad header note.

include <lib/params.scad>

// Which half's footprint/inset to size the shim block against.
SHIM_FOOTPRINT = FOOT_L;     // swap to FOOT_R when generating right-half shims
BLOCK_XY = [20, 20];         // plan size of each corner block

// Selected tenting angle for THIS render (degrees). Override at the CLI with
// `openscad -D TENT_ANGLE_DEG=16 ...` to generate a different angle's set.
TENT_ANGLE_DEG = 12;

function corner_span_x(footprint, inset) = footprint[0] - 2 * inset[0];

module tenting_shim_block(h) {
    difference() {
        // simple flat-top, flat-bottom block; height h is a straight
        // extrusion (angle comes from choosing different h per corner, not
        // from an angled face) — keeps this a trivially printable, low-risk
        // part with no critical-alignment sloped surfaces.
        cube([BLOCK_XY[0], BLOCK_XY[1], h], center = true);
        translate([0, 0, -0.1])
            cylinder(h = h + 0.2, d = M3_CLR_D, $fn = 24);
        // counterbore for bolt head on the underside (tray-facing) face
        translate([0, 0, -h / 2])
            cylinder(h = M3_HEAD_H, d = M3_HEAD_D, $fn = 32);
    }
}

delta_h = corner_span_x(SHIM_FOOTPRINT, CORNER_INSET) * tan(TENT_ANGLE_DEG);
h_low = SHIM_BASE_H;
h_high = SHIM_BASE_H + delta_h;

echo(str("tent angle (deg) = ", TENT_ANGLE_DEG));
echo(str("low-side shim height (mm) = ", h_low));
echo(str("high-side shim height (mm) = ", h_high));

// Lay the 4-block set flat for a single print job:
// left column = 2x low blocks, right column = 2x high blocks.
gap = 6;
for (i = [0, 1]) {
    translate([i * (BLOCK_XY[0] + gap), 0, h_low / 2])
        tenting_shim_block(h_low);
    translate([i * (BLOCK_XY[0] + gap), BLOCK_XY[1] + gap, h_high / 2])
        tenting_shim_block(h_high);
}
