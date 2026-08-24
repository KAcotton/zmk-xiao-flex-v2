"""Numerically determine available in-case vertical clearance for a
vertical 18650 battery bay, near the thumb-cluster / inner (most-tented)
edge of each half. Uses real ray-cast intersection against the case shell
solid (not bounding-box guesses) plus 3D XY-footprint overlap checks
against every other solid (key sockets, sensor mount, bosses).

Read-only; writes nothing. Run headlessly:
  & 'C:\\Program Files\\FreeCAD 1.1\\bin\\freecadcmd.exe' '_battery_bay_clearance_scan.py'
"""
import FreeCAD, Part, math

files = {
    "LEFT": (r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylleft.step", +1),
    "RIGHT": (r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylright.step", -1),
}

CELL_DIA = 18.6
CELL_LEN = 65.5
PROBE_R = CELL_DIA / 2.0 + 1.5   # candidate bore radius incl. wall/slop for the scan
RAY_TOP = 200.0


def ceiling_clearance(shell, cx, cy, z0=3.0):
    """First Z (>= z0) at which a vertical probe ray hits the shell solid,
    via real edge/solid boolean intersection (not a bbox guess)."""
    edge = Part.makeLine(FreeCAD.Vector(cx, cy, z0), FreeCAD.Vector(cx, cy, RAY_TOP))
    common = edge.common(shell)
    zs = []
    for e in common.Edges:
        zs.append(e.BoundBox.ZMin)
    if not zs:
        return None  # ray never re-entered the shell -- no ceiling found in range
    return min(zs)


def bbox_maybe_overlaps(bb, cx, cy, r):
    """Cheap reject: True means 'might overlap, needs real check'; False means
    definitely clear (bbox itself doesn't reach the probe circle)."""
    nx = max(bb.XMin - cx, 0, cx - bb.XMax)
    ny = max(bb.YMin - cy, 0, cy - bb.YMax)
    return math.hypot(nx, ny) <= r


def real_overlap(solid, cx, cy, r, z0, z1):
    """Confirm true 3D overlap (not just bbox) via boolean common with a
    vertical probe cylinder, since some case solids have NURBS/spline faces
    whose reported BoundBox is much larger than their actual material."""
    probe = Part.makeCylinder(r, z1 - z0, FreeCAD.Vector(cx, cy, z0))
    common = probe.common(solid)
    return common.Volume > 1.0  # mm^3 tolerance


for label, (path, inner_sign) in files.items():
    print("=" * 78)
    print(f"{label}  inner_sign={inner_sign}")
    shape = Part.Shape()
    shape.read(path)
    solids = shape.Solids

    plate = None
    plate_area = 0.0
    for s in solids:
        for f in s.Faces:
            surf = f.Surface
            if surf.__class__.__name__ == "Plane" and f.Area > 10000:
                n = FreeCAD.Vector(surf.Axis.x, surf.Axis.y, surf.Axis.z)
                n.normalize()
                if abs(n.z) > 0.999 and abs(f.BoundBox.ZMin) < 0.5:
                    if f.Area > plate_area:
                        plate_area = f.Area
                        plate = s
    plate_bb = plate.BoundBox

    no_flat = []
    for s in solids:
        if s is plate:
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
    shell = no_flat[0]
    others = no_flat[1:]  # key sockets, sensor mount, misc bosses -- NOT plate, NOT shell
    print(f"shell vol={shell.Volume:.0f}mm3  {len(others)} other (non-shell,non-plate) solids")

    inner_edge_x = plate_bb.XMax if inner_sign > 0 else plate_bb.XMin

    # identify the odd large-volume "other" solid (not shell/plate/small sockets)
    for s in others:
        if s.Volume > 5000:
            print(f"large non-shell solid: vol={s.Volume:.0f}mm3 bbox X[{s.BoundBox.XMin:.1f},{s.BoundBox.XMax:.1f}] "
                  f"Y[{s.BoundBox.YMin:.1f},{s.BoundBox.YMax:.1f}] Z[{s.BoundBox.ZMin:.1f},{s.BoundBox.ZMax:.1f}]")

    # thumb-cluster region: sockets of ~standard finger-key volume (800-1900mm3)
    # spatially offset (low Y) from the main Y>0 finger-matrix block. Exclude
    # oversized structural/sensor-mount solids from this envelope.
    thumb_ys = [s.BoundBox for s in others if s.BoundBox.YMin < 10 and 500 < s.Volume < 2000]
    if thumb_ys:
        ty0 = min(b.YMin for b in thumb_ys)
        ty1 = max(b.YMax for b in thumb_ys)
        tx0 = min(b.XMin for b in thumb_ys)
        tx1 = max(b.XMax for b in thumb_ys)
        print(f"thumb-region (Y<10) solids envelope: X[{tx0:.1f},{tx1:.1f}] Y[{ty0:.1f},{ty1:.1f}]")

    # Scan a grid near the inner edge, spanning the thumb-region Y band and
    # a bit beyond, to find a spot with enough ceiling clearance AND no XY
    # overlap (any Z) with any other solid.
    x_candidates = [inner_edge_x - inner_sign * d for d in (2, 10, 20, 30, 40)]
    y_lo = plate_bb.YMin + PROBE_R + 1
    y_hi = plate_bb.YMax - PROBE_R - 1
    y_candidates = [y for y in range(int(y_lo), int(y_hi), 8)]

    print(f"\nScanning inner-edge x-offsets against y in [{y_lo:.1f},{y_hi:.1f}] step 4mm ...")
    best = None
    results = []
    probe_z0, probe_z1 = 3.0, 90.0
    for cx in x_candidates:
        for cy in y_candidates:
            # first find the real ceiling via ray-cast against the shell
            ceil_z = ceiling_clearance(shell, cx, cy)
            if ceil_z is None:
                continue
            overlap_hit = False
            for s in others:
                if not bbox_maybe_overlaps(s.BoundBox, cx, cy, PROBE_R):
                    continue
                if real_overlap(s, cx, cy, PROBE_R, probe_z0, min(ceil_z, probe_z1)):
                    overlap_hit = True
                    break
            if overlap_hit:
                continue
            clearance = ceil_z - 3.0
            results.append((cx, cy, clearance))
            if best is None or clearance > best[2]:
                best = (cx, cy, clearance)

    # report top candidates near the thumb Y-band specifically
    if thumb_ys:
        band = [r for r in results if ty0 - 10 <= r[1] <= ty1 + 10]
        band.sort(key=lambda r: -r[2])
        print(f"Top clearances within thumb Y-band [{ty0-10:.1f},{ty1+10:.1f}], no XY overlap with any socket/sensor solid:")
        for cx, cy, clr in band[:8]:
            print(f"  (x={cx:.1f}, y={cy:.1f}) -> clearance={clr:.1f}mm  {'OK >=65.5' if clr >= 65.5 else 'insufficient'}")

    results.sort(key=lambda r: -r[2])
    print(f"\nOverall best (any y) clearance found near inner edge:")
    for cx, cy, clr in results[:5]:
        print(f"  (x={cx:.1f}, y={cy:.1f}) -> clearance={clr:.1f}mm")

    if best:
        print(f"\nBEST overall: x={best[0]:.1f} y={best[1]:.1f} clearance={best[2]:.1f}mm "
              f"(need >= {CELL_LEN + 2:.1f}mm for cell+slop)")
    else:
        print("\nNo valid (non-overlapping, ceiling-found) candidate in scanned grid.")

print("\nDONE")
