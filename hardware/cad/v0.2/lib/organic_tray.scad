// TylerDactyl v0.2 modular baseplate — organic-footprint tray.
// Include params_v2.scad and organic_outline.scad before this file.
//
// Builds an open-top tray whose PLAN-VIEW outline is the real CASE
// footprint (via projection(), see organic_outline.scad) instead of a
// rectangular bounding box. The tray floor + wall ring are 2D-extruded from
// that real outline; the battery pocket, corner posts, and controller
// shelf are ordinary primitive CSG (cylinders/cubes), which is always safe
// regardless of the CASE mesh's non-manifold status.
//
// KNOWN LIMITATION (see design notes): this tray's TOP FACE is flat/planar
// at z=0. The real CASE's bottom rim is NOT flat — it is an organic,
// per-column contoured surface (confirmed by sampling near-bottom vertices
// across the mesh: low points are found scattered across nearly the whole
// footprint, not confined to a narrow flat perimeter band). A flat-topped
// tray will therefore NOT flush-seal against the real case bottom rim
// everywhere; it will only contact at the lowest points and leave gaps
// elsewhere. This is flagged, not solved, in this pass — see the design
// notes "open questions" for what a human needs to do about it in a real
// CAD tool.

// side: "left" | "right"
// battery_pos: [x, y, z] center of the battery pocket capsule, in the
//              outline's own coordinate frame (same frame as the STL).
// controller_pos: [x, y] center of the nice!nano v2 shelf.
module organic_tray(side, battery_pos, controller_pos) {
    difference() {
        union() {
            // floor: full real outline, thin
            linear_extrude(height = FLOOR)
                case_outline(side);
            // wall ring: outline minus wall-thickness-inset outline,
            // extruded to full tray depth (open top).
            linear_extrude(height = TRAY_DEPTH)
                difference() {
                    case_outline(side);
                    offset(delta = -WALL) case_outline(side);
                }
        }

        // battery pocket: horizontal capsule bore for the 18650 cell +
        // JST clearance. NOT verified against real local wall thickness at
        // this XY location (the outline is organic, not uniform width) —
        // inspect the render before trusting this pocket doesn't breach a
        // thin section of the real outline.
        translate(battery_pos)
            rotate([0, 90, 0])
                hull() {
                    translate([0, 0, -(POCKET_LEN / 2 - POCKET_DIA / 2)])
                        sphere(d = POCKET_DIA, $fn = 32);
                    translate([0, 0, (POCKET_LEN / 2 - POCKET_DIA / 2)])
                        sphere(d = POCKET_DIA, $fn = 32);
                }

        // corner mounting-post through-holes (placeholder positions, see
        // params_v2.scad CORNER_INSET note)
        for (c = corner_xy(side))
            translate([c[0], c[1], -0.1])
                cylinder(h = TRAY_DEPTH + 0.2, d = M3_CLR_D, $fn = 24);
    }

    // corner mounting posts (solid, sit inside the wall ring)
    for (c = corner_xy(side))
        translate([c[0], c[1], 0])
            difference() {
                cylinder(h = TRAY_DEPTH, d = M3_BOSS_D, $fn = 32);
                translate([0, 0, -0.1]) cylinder(h = TRAY_DEPTH + 0.2, d = M3_CLR_D, $fn = 24);
            }

    // controller shelf: 4 short standoffs sized for nice!nano v2
    ctl_w = NICE_NANO[0];
    ctl_l = NICE_NANO[1];
    for (sx = [-1, 1])
        for (sy = [-1, 1])
            translate([controller_pos[0] + sx * (ctl_w / 2 - 2),
                       controller_pos[1] + sy * (ctl_l / 2 - 2),
                       FLOOR])
                cylinder(h = 3, d = 2.6, $fn = 16);
}

// Corner post XY positions, inset from the REAL (non-origin-centered) bbox
// corners (PLACEHOLDER — see CORNER_INSET note in params_v2.scad).
function corner_xy(side) =
    let (mn = side == "left" ? FOOT_L_MIN : FOOT_R_MIN,
         mx = side == "left" ? FOOT_L_MAX : FOOT_R_MAX)
    [[mx[0] - CORNER_INSET[0], mx[1] - CORNER_INSET[1]],
     [mn[0] + CORNER_INSET[0], mx[1] - CORNER_INSET[1]],
     [mn[0] + CORNER_INSET[0], mn[1] + CORNER_INSET[1]],
     [mx[0] - CORNER_INSET[0], mn[1] + CORNER_INSET[1]]];
