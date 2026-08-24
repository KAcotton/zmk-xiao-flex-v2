"""v0.3 baseplate generator: tenting feet + vertical 18650 battery turret.

Ground truth used (verified via _register_analysis.py and the
_battery_bay_* analysis scripts in v0.3-source/ against the real STEP
B-rep, NOT the STL bounding boxes):
  - The PLATE solid in each STEP file is the flat Z=0..3mm sheet whose
    footprint exactly matches the previously-measured STL bbox
    (LEFT 149.03x144.75mm, RIGHT 167.00x158.31mm).
  - The plate has 8 through clearance holes (r=1.7mm, Z 1.45-3.00) that
    line up with matching r=2.15mm blind holes (Z 3.00-8.00) in 7 of the
    case's internal boss solids -- these are the existing case<->plate
    fastener positions.
  - Every case-side solid (main shell, per-key sockets, sensor mount) has
    ZMin >= 2.63mm. The tenting feet are built entirely at Z <= 0, so they
    cannot geometrically intersect any of them -- verified below by
    explicit assertion.
  - BATTERY LOCATION CHANGE (this revision): the battery moved from a
    below-plate pod (Z<=0, cell lying on Y) to a vertical cell standing
    with its axis parallel to Z. Real ray-cast + boolean-overlap scans
    (see v0.3-source/_battery_bay_*.py) proved this vertical cell CANNOT
    fit inside the existing case interior, anywhere on either half:
      * Near the thumb cluster / inner edge specifically, the case shell
        is only ~0-8mm tall above the plate (it's the low perimeter edge)
        -- nowhere near the ~67.5mm needed.
      * Scanning the ENTIRE plate footprint on a coarse grid, checking
        real boolean overlap (not bbox) against every key-socket/sensor
        solid, the tallest fully-clear interior column found anywhere was
        only ~26.8mm (LEFT) / ~26.4mm (RIGHT) -- still short of 67.5mm.
      * A finer 2D scan restricted to within 50mm of the inner edge found
        ZERO XY sites on LEFT with a 22.6mm-diameter footprint clear of
        every key-socket solid at any Y; RIGHT found sites only 63mm+ away
        from the thumb cluster's centroid (i.e. not "near the thumb
        cluster" either).
    Conclusion: an in-case bay is not geometrically achievable at the
    requested location without deleting/relocating a key socket. Instead,
    this revision builds the battery bay as a separate, additive vertical
    turret mounted OUTSIDE the case's existing footprint, immediately
    outboard of the inner (most-tented) edge at the thumb cluster's Y
    position -- new material, not carved from existing interior volume,
    so it cannot collide with any key-socket/sensor solid by construction
    (verified below). It requires a case-shell wall penetration (small
    wire-pass hole) at the attachment point -- explicitly authorized by
    the user for this revision. See design notes for full numbers.

Run headlessly:
  & 'C:\\Program Files\\FreeCAD 1.1\\bin\\freecadcmd.exe' 'build_v03.py'
"""
import os
import math
import itertools
import FreeCAD, Part, Mesh

SRC_DIR = r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source"
OUT_DIR = r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3"

HALVES = {
    "left": os.path.join(SRC_DIR, "cosmotylleft.step"),
    "right": os.path.join(SRC_DIR, "cosmotylright.step"),
}

TENT_ANGLES_DEG = [8.0, 14.0, 20.0]   # min / mid / max of requested 8-20deg range
MIN_FOOT_HEIGHT = 10.0                # mm, shortest foot standoff (structural minimum)
FOOT_XY = 15.0                        # mm, square foot footprint size
FOOT_HOLE_R = 1.75                    # mm, reuse plate's own M3 clearance hole (r=1.7) + slop

CELL_DIA = 18.6                       # mm, 18650 nominal + wrap
CELL_LEN = 65.5                       # mm, 18650 nominal (flat-top) + slop
TURRET_WALL = 2.0                     # mm, turret side/floor wall thickness
TURRET_OUTER_R = CELL_DIA / 2.0 + TURRET_WALL       # 11.3mm
TURRET_HEIGHT = CELL_LEN + 2 * TURRET_WALL          # 69.5mm, from plate-top Z=3 upward
TURRET_ATTACH_OVERLAP = 3.0            # mm the turret embeds past the plate's true inner edge, for a solid mounting flange bond
WIRE_HOLE_R = 3.0                      # mm, battery-lead pass-through into the case interior
WIRE_HOLE_Z = 3.0 + TURRET_WALL + 6.0   # mm, low in the turret, just above its floor
WIRE_HOLE_LEN = 30.0                    # mm, long enough to fully pierce the turret wall + reach case interior air


def get_plate_and_holes(shape):
    """Return (plate_solid, plate_bbox, [ (x,y) clearance-hole centers, r=1.7mm ])."""
    plate = None
    plate_area = 0.0
    for s in shape.Solids:
        for f in s.Faces:
            surf = f.Surface
            if surf.__class__.__name__ == "Plane" and f.Area > 10000:
                n = FreeCAD.Vector(surf.Axis.x, surf.Axis.y, surf.Axis.z)
                n.normalize()
                if abs(n.z) > 0.999 and abs(f.BoundBox.ZMin) < 0.5:
                    if f.Area > plate_area:
                        plate_area = f.Area
                        plate = s
    if plate is None:
        raise RuntimeError("Could not identify plate solid (Z=0 flat face > 10000mm^2 not found)")

    holes = []
    for f in plate.Faces:
        surf = f.Surface
        if surf.__class__.__name__ == "Cylinder" and 1.5 <= surf.Radius <= 2.0:
            fb = f.BoundBox
            if fb.ZMin >= 1.0 and fb.ZMax <= 3.5:
                cx = (fb.XMin + fb.XMax) / 2.0
                cy = (fb.YMin + fb.YMax) / 2.0
                holes.append((cx, cy))
    return plate, plate.BoundBox, holes


def get_case_boss_zmins(shape, plate_solid):
    """ZMin of every non-plate solid, to prove our Z<=0 parts can't collide."""
    zmins = []
    for s in shape.Solids:
        if s is plate_solid:
            continue
        zmins.append(s.BoundBox.ZMin)
    return zmins


def best_triangle(points):
    """Pick 3 points maximizing triangle area (max-spread 3-point support)."""
    best = None
    best_area = -1.0
    for combo in itertools.combinations(points, 3):
        (x1, y1), (x2, y2), (x3, y3) = combo
        area = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2.0
        if area > best_area:
            best_area = area
            best = combo
    return best, best_area


def build_feet(holes, feet_pts, angle_deg, inner_sign):
    """Return dict of foot solids keyed by hole XY, heights chosen so the
    plane through the 3 feet tilts by angle_deg about a Y-parallel axis,
    height increasing toward the 'inner' (thumb/centerline) side.
    inner_sign = +1 if inner side is +X (LEFT half), -1 if inner side is -X (RIGHT half).
    """
    tan_a = math.tan(math.radians(angle_deg))
    raw_heights = {p: inner_sign * p[0] * tan_a for p in feet_pts}
    min_raw = min(raw_heights.values())
    offset = MIN_FOOT_HEIGHT - min_raw
    heights = {p: raw_heights[p] + offset for p in feet_pts}

    solids = {}
    for (x, y), h in heights.items():
        box = Part.makeBox(FOOT_XY, FOOT_XY, h, FreeCAD.Vector(x - FOOT_XY / 2, y - FOOT_XY / 2, -h))
        hole = Part.makeCylinder(FOOT_HOLE_R, h + 2, FreeCAD.Vector(x, y, -h - 1))
        foot = box.cut(hole)
        solids[(x, y)] = (foot, h)
    return solids, heights


def get_shell_and_others(shape, plate_solid):
    """Split all non-plate solids into (shell, others). shell = the
    largest-volume solid with no level (<=0.5deg from horizontal) planar
    face -- the main case body. others = every remaining solid: per-key
    switch sockets, the trackball/encoder sensor mount, and misc bosses."""
    no_flat = []
    for s in shape.Solids:
        if s is plate_solid:
            continue
        has_flat = any(
            f.Surface.__class__.__name__ == "Plane"
            and abs(FreeCAD.Vector(f.Surface.Axis.x, f.Surface.Axis.y, f.Surface.Axis.z).normalize().z) > 0.999
            and abs(f.BoundBox.ZMin) < 0.5
            for f in s.Faces
        )
        if not has_flat:
            no_flat.append(s)
    no_flat.sort(key=lambda s: -s.Volume)
    return no_flat[0], no_flat[1:]


def find_turret_site(others, plate_bb, inner_edge_x, inner_sign):
    """Locate the vertical battery turret's (cx,cy): outboard of the plate's
    inner (most-tented) edge, at the thumb cluster's Y position, per the
    real-geometry finding that no in-case column is tall enough (see module
    docstring). Being entirely outside the plate's inner edge in X, the
    turret's footprint cannot overlap any interior key-socket/sensor solid
    by construction -- this is confirmed (not assumed) by the caller via
    boolean checks against every 'others' solid after the solid is built."""
    thumb = [s.BoundBox for s in others if s.BoundBox.YMin < 10 and 500 < s.Volume < 2000]
    if not thumb:
        raise RuntimeError("Could not identify thumb-cluster key-socket solids (Y<10, 500-2000mm^3 volume)")
    ty0 = min(b.YMin for b in thumb)
    ty1 = max(b.YMax for b in thumb)
    cy = (ty0 + ty1) / 2.0
    cx = inner_edge_x + inner_sign * (TURRET_OUTER_R - TURRET_ATTACH_OVERLAP)
    return cx, cy, (ty0, ty1)


def build_battery_turret(cx, cy, inner_sign, shell, others):
    """Vertical 18650 turret: cell axis parallel to Z, mounted OUTSIDE the
    existing case footprint (see module docstring for why an in-case bay
    isn't achievable). Open top for cell insertion (needs a user-supplied
    screw/snap cap, not modeled -- see design notes open questions). A
    radial wire-pass hole near the floor connects the cell cavity to the
    case interior through the shell wall it partially overlaps."""
    outer = Part.makeCylinder(TURRET_OUTER_R, TURRET_HEIGHT, FreeCAD.Vector(cx, cy, 3.0))
    bore = Part.makeCylinder(
        CELL_DIA / 2.0, TURRET_HEIGHT - TURRET_WALL + 1,
        FreeCAD.Vector(cx, cy, 3.0 + TURRET_WALL),
    )
    body = outer.cut(bore)

    # wire-pass hole: drilled from the bore center toward the case interior
    # (i.e. toward -inner_sign*X, back across the plate's inner edge), long
    # enough to clear the turret's inward wall and reach open case-interior
    # air on the other side.
    wire_origin = FreeCAD.Vector(cx, cy, WIRE_HOLE_Z)
    wire_axis = FreeCAD.Vector(-inner_sign, 0, 0)
    wire_hole = Part.makeCylinder(WIRE_HOLE_R, WIRE_HOLE_LEN, wire_origin, wire_axis)
    body = body.cut(wire_hole)

    overlap_others_vol = sum(body.common(s).Volume for s in others)
    overlap_shell_vol = body.common(shell).Volume
    return body, overlap_others_vol, overlap_shell_vol


def process_half(name, step_path, inner_sign):
    print("=" * 78)
    print(f"{name.upper()}")
    shape = Part.Shape()
    shape.read(step_path)

    plate, plate_bb, holes = get_plate_and_holes(shape)
    print(f"Plate footprint: X[{plate_bb.XMin:.2f},{plate_bb.XMax:.2f}] "
          f"Y[{plate_bb.YMin:.2f},{plate_bb.YMax:.2f}]  clearance holes found: {len(holes)}")
    assert len(holes) >= 7, "expected >=7 real mounting holes on plate"

    other_zmins = get_case_boss_zmins(shape, plate)
    min_other_z = min(other_zmins)
    print(f"Min ZMin over all {len(other_zmins)} non-plate solids: {min_other_z:.3f}mm "
          f"(our parts live at Z<=0, so no collision is possible)")

    feet_pts, tri_area = best_triangle(holes)
    print(f"Chosen 3 feet points (max-spread triangle, area={tri_area:.0f}mm^2): {feet_pts}")

    # Vertical battery turret: mounted outboard of the case, next to the thumb
    # cluster on the most-tented edge (see module docstring - an in-case bay
    # was proven geometrically impossible for a standing 18650 on this shape).
    inner_edge_x = plate_bb.XMax if inner_sign > 0 else plate_bb.XMin
    shell, others = get_shell_and_others(shape, plate)
    turret_cx, turret_cy, thumb_y_range = find_turret_site(others, plate_bb, inner_edge_x, inner_sign)
    print(f"Turret site: center=({turret_cx:.1f},{turret_cy:.1f})  "
          f"thumb-cluster Y range used: {thumb_y_range}")

    doc = FreeCAD.newDocument(f"tylerdactyl_v03_{name}")
    half_dir = os.path.join(OUT_DIR, name)
    os.makedirs(half_dir, exist_ok=True)

    # reference-only import of the real case/plate so the FCStd shows context,
    # not just the new parts - not used for any boolean/collision math above.
    ref_obj = doc.addObject("Part::Feature", f"{name}_case_reference")
    ref_obj.Shape = shape
    if FreeCAD.GuiUp:
        ref_obj.ViewObject.Transparency = 70
        ref_obj.ViewObject.ShapeColor = (0.6, 0.6, 0.6)

    all_ok = True

    # Turret geometry doesn't depend on tenting angle (it's built directly off
    # the plate's Z=3 top face, outboard of the case), so build/verify it once.
    turret, overlap_others_vol, overlap_shell_vol = build_battery_turret(
        turret_cx, turret_cy, inner_sign, shell, others
    )
    turret_ok = turret.isValid() and turret.Volume > 0 and overlap_others_vol < 1.0
    if not turret_ok:
        print(f"  INVALID/overlapping turret: valid={turret.isValid()} vol={turret.Volume:.0f}mm3 "
              f"overlap_vs_others={overlap_others_vol:.1f}mm3")
        all_ok = False
    print(f"  battery turret: center=({turret_cx:.1f},{turret_cy:.1f}) "
          f"height={TURRET_HEIGHT:.1f}mm (Z {3.0:.1f}->{3.0 + TURRET_HEIGHT:.1f}) "
          f"valid={turret.isValid()} vol={turret.Volume:.0f}mm3 "
          f"overlap_vs_key_sockets/sensor={overlap_others_vol:.2f}mm3 "
          f"overlap_vs_case_shell={overlap_shell_vol:.2f}mm3 (expected >0: wire hole + mounting flange bond)")

    turret_stl = os.path.join(half_dir, f"{name}_battery_turret.stl")
    Mesh.Mesh(turret.tessellate(0.1)).write(turret_stl)
    print(f"  wrote {turret_stl}")

    turret_obj = doc.addObject("Part::Feature", f"{name}_battery_turret")
    turret_obj.Shape = turret

    for angle in TENT_ANGLES_DEG:
        feet_solids, heights = build_feet(holes, feet_pts, angle, inner_sign)

        fused_feet = None
        for (x, y), (foot, h) in feet_solids.items():
            if not foot.isValid() or foot.Volume <= 0:
                print(f"  INVALID foot solid at ({x:.1f},{y:.1f}), angle={angle}")
                all_ok = False
            fused_feet = foot if fused_feet is None else fused_feet.fuse(foot)

        assert fused_feet.BoundBox.ZMax <= 0.001, "foot geometry leaked above Z=0"
        print(f"  angle={angle:.1f}deg  foot heights: "
              + ", ".join(f"({x:.1f},{y:.1f})={h:.1f}mm" for (x, y), h in heights.items())
              + f"  fused_valid={fused_feet.isValid()}  vol={fused_feet.Volume:.0f}mm3")

        stl_path = os.path.join(half_dir, f"{name}_feet_{int(angle)}deg.stl")
        Mesh.Mesh(fused_feet.tessellate(0.1)).write(stl_path)
        print(f"  wrote {stl_path}")

        obj2 = doc.addObject("Part::Feature", f"{name}_feet_{int(angle)}deg")
        obj2.Shape = fused_feet

    doc.recompute()
    fcstd_path = os.path.join(half_dir, f"{name}_v03.FCStd")
    doc.saveAs(fcstd_path)
    print(f"  wrote {fcstd_path}")
    FreeCAD.closeDocument(doc.Name)

    return all_ok


os.makedirs(OUT_DIR, exist_ok=True)
results = {}
results["left"] = process_half("left", HALVES["left"], inner_sign=+1)
results["right"] = process_half("right", HALVES["right"], inner_sign=-1)
print("=" * 78)
print("RESULTS:", results)
print("DONE")
