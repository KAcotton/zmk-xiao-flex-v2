"""Full-footprint interior-clearance heatmap (coarse grid) to find where the
case shell is tallest, independent of the thumb-cluster/inner-edge
constraint -- used to judge whether a boss/bump-out near the thumb cluster
is small (few mm) or impractically large (tens of mm) versus relocating.

Read-only. Run headlessly:
  & 'C:\\Program Files\\FreeCAD 1.1\\bin\\freecadcmd.exe' '_battery_bay_full_scan.py'
"""
import FreeCAD, Part, math

files = {
    "LEFT": r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylleft.step",
    "RIGHT": r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylright.step",
}

PROBE_R = 18.6 / 2.0 + 1.5
RAY_TOP = 200.0
GRID_STEP = 15.0


def ceiling_clearance(shell, cx, cy, z0=3.0):
    edge = Part.makeLine(FreeCAD.Vector(cx, cy, z0), FreeCAD.Vector(cx, cy, RAY_TOP))
    common = edge.common(shell)
    zs = [e.BoundBox.ZMin for e in common.Edges]
    return min(zs) - z0 if zs else None


def bbox_maybe_overlaps(bb, cx, cy, r):
    nx = max(bb.XMin - cx, 0, cx - bb.XMax)
    ny = max(bb.YMin - cy, 0, cy - bb.YMax)
    return math.hypot(nx, ny) <= r


def real_overlap(solid, cx, cy, r, z0, z1):
    probe = Part.makeCylinder(r, z1 - z0, FreeCAD.Vector(cx, cy, z0))
    return probe.common(solid).Volume > 1.0


for label, path in files.items():
    print("=" * 78, flush=True)
    print(label, flush=True)
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
    others = no_flat[1:]

    x_lo, x_hi = plate_bb.XMin + 10, plate_bb.XMax - 10
    y_lo, y_hi = plate_bb.YMin + 10, plate_bb.YMax - 10

    best = None
    all_results = []
    x = x_lo
    while x <= x_hi:
        y = y_lo
        while y <= y_hi:
            ceil = ceiling_clearance(shell, x, y)
            if ceil is not None:
                overlap = False
                for s in others:
                    if bbox_maybe_overlaps(s.BoundBox, x, y, PROBE_R) and real_overlap(s, x, y, PROBE_R, 3.0, min(ceil + 3, 90)):
                        overlap = True
                        break
                if not overlap:
                    all_results.append((x, y, ceil))
                    if best is None or ceil > best[2]:
                        best = (x, y, ceil)
            y += GRID_STEP
        x += GRID_STEP
        print(f"  row x={x:.0f} done, {len(all_results)} clear pts so far", flush=True)

    all_results.sort(key=lambda r: -r[2])
    print(f"Top 10 clearances anywhere on the plate footprint (no socket/sensor overlap):")
    for x, y, c in all_results[:10]:
        print(f"  (x={x:.1f}, y={y:.1f}) clearance={c:.1f}mm")
    print(f"Global best: {best}")

print("\nDONE")
