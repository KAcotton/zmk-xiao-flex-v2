"""Cheap full-footprint interior-height heatmap: ceiling clearance from the
shell only (no per-solid overlap check yet -- that's applied afterward only
at the winning candidate). Much faster; used to find where the case is
tallest at all before worrying about socket/sensor collisions there.
"""
import FreeCAD, Part

files = {
    "LEFT": r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylleft.step",
    "RIGHT": r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylright.step",
}
RAY_TOP = 200.0
GRID_STEP = 10.0


def ceiling_clearance(shell, cx, cy, z0=3.0):
    edge = Part.makeLine(FreeCAD.Vector(cx, cy, z0), FreeCAD.Vector(cx, cy, RAY_TOP))
    common = edge.common(shell)
    zs = [e.BoundBox.ZMin for e in common.Edges]
    return min(zs) - z0 if zs else None


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

    x_lo, x_hi = plate_bb.XMin + 10, plate_bb.XMax - 10
    y_lo, y_hi = plate_bb.YMin + 10, plate_bb.YMax - 10
    results = []
    x = x_lo
    while x <= x_hi:
        y = y_lo
        while y <= y_hi:
            c = ceiling_clearance(shell, x, y)
            if c is not None:
                results.append((x, y, c))
            y += GRID_STEP
        x += GRID_STEP
        print(f"  row x={x:.0f} done, {len(results)} pts so far", flush=True)

    results.sort(key=lambda r: -r[2])
    print(f"Top 15 ceiling clearances (shell only, sockets not yet excluded):")
    for x, y, c in results[:15]:
        print(f"  (x={x:.1f}, y={y:.1f}) clearance={c:.1f}mm")

print("DONE", flush=True)
