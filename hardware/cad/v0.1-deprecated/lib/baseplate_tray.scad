// TylerDactyl v0.1 modular baseplate — shared tray module.
// Include lib/params.scad before this file.
//
// Produces a deep open-top tray that bolts under the existing (unmodified)
// CASE bottom rim via a set of interchangeable tenting shims (see
// tenting_shim.scad). The tray houses the 18650 cell + holder, a socketed
// nice!nano v2, a panel power switch cutout, and a flex-cable pass-through
// slot up to the existing key-matrix PCB/holder.
//
// All corner/keepout placements not explicitly measured from the v1 meshes
// are marked ASSUMPTION and are meant to be revisited once real hole
// positions / cutout locations are confirmed.

module corner_post(h, d = M3_BOSS_D, hole_d = M3_CLR_D) {
    difference() {
        cylinder(h = h, d = d, $fn = 32);
        translate([0, 0, -0.1]) cylinder(h = h + 0.2, d = hole_d, $fn = 24);
    }
}

// footprint: [W, D] outer size, centered at origin in X/Y.
// battery_edge: "back" | "front" — which long edge the cell bay runs along.
// controller_corner: [sx, sy] each +-1, which corner the controller shelf sits in.
// keepout: optional [ [W,D,H], [cx,cy] ] visual-only keepout box (e.g. trackball
//          clearance on the right half) — rendered with % so it does not cut
//          into the solid; purely a flag for the human modeler/reviewer.
module baseplate_tray(footprint, corner_inset, battery_edge = "back",
                       controller_corner = [1, -1], keepout = undef) {
    W = footprint[0];
    D = footprint[1];
    H = TRAY_DEPTH;

    ix = W / 2 - corner_inset[0];
    iy = D / 2 - corner_inset[1];
    corner_xy = [[ ix,  iy], [-ix,  iy], [-ix, -iy], [ ix, -iy]];

    difference() {
        union() {
            // outer shell + floor in one cut: side walls are WALL thick,
            // floor is FLOOR thick, top stays open.
            difference() {
                cube([W, D, H], center = true);
                translate([0, 0, FLOOR])
                    cube([W - 2 * WALL, D - 2 * WALL, H], center = true);
            }
            // corner mounting posts, full tray height, flush with top rim
            for (c = corner_xy)
                translate([c[0], c[1], -H / 2])
                    corner_post(h = H);
        }

        // through-holes in the corner posts for the tenting-shim / case bolt
        for (c = corner_xy)
            translate([c[0], c[1], -H / 2 - 0.1])
                cylinder(h = H + 0.2, d = M3_CLR_D, $fn = 24);

        // panel power-switch slot, centered on the -Y (front) outer wall
        translate([0, -D / 2, -H / 2 + 6])
            cube([10, WALL * 2 + 1, 4], center = true);

        // flex-cable pass-through slot, centered on the +Y (back, holder-side)
        // top rim. ASSUMPTION: aligns under the existing HOLDER connector —
        // confirm exact position once the rigid-flex PCB stack-up is defined.
        translate([0, D / 2 - WALL / 2, H / 2 - 3])
            cube([20, WALL * 2 + 1, 3], center = true);
    }

    // --- battery bay retention bosses (2 pairs, bracketing a commercial
    // single-cell holder screwed to the floor) ---
    bat_w = CELL_HOLDER_ENV[0];
    bat_l = CELL_HOLDER_ENV[1];
    bat_y = battery_edge == "back"
        ? D / 2 - WALL - bat_w / 2 - 2
        : -(D / 2 - WALL - bat_w / 2 - 2);
    for (dx = [-1, 1])
        translate([dx * (bat_l / 2 - 4), bat_y, -H / 2 + FLOOR])
            cylinder(h = 4, d = 3.2, $fn = 20); // M2 self-tap boss for holder screw

    // --- controller shelf: 4 short standoffs sized for nice!nano v2 ---
    ctl_w = NICE_NANO[0];
    ctl_l = NICE_NANO[1];
    ctl_x = controller_corner[0] * (W / 2 - corner_inset[0] - ctl_w / 2 - 3);
    ctl_y = controller_corner[1] * (D / 2 - corner_inset[1] - ctl_l / 2 - 3);
    for (sx = [-1, 1])
        for (sy = [-1, 1])
            translate([ctl_x + sx * (ctl_w / 2 - 2),
                       ctl_y + sy * (ctl_l / 2 - 2),
                       -H / 2 + FLOOR])
                cylinder(h = 3, d = 2.6, $fn = 16); // M2 standoff for socket/board

    // --- optional visual-only keepout marker (not subtracted from solid) ---
    if (!is_undef(keepout)) {
        size = keepout[0];
        center = keepout[1];
        %translate([center[0], center[1], 0])
            cube([size[0], size[1], size[2]], center = true);
    }
}
