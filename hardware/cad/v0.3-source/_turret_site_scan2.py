"""2D scan (X and Y) near the inner edge for a turret footprint location
with zero real overlap against key-socket/sensor solids (shell overlap OK).
Reports the valid location closest to the thumb-cluster centroid.
"""
import FreeCAD, Part, math

files = {
    "LEFT": (r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylleft.step", +1),
    "RIGHT": (r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylright.step", -1),
}

CELL_DIA = 18.6
CELL_LEN = 65.5
WALL = 2.0
OUTER_R = CELL_DIA / 2.0 + WALL
HEIGHT = CELL_LEN + 2 * WALL


def bbox_maybe(bb, cx, cy, r):
    nx = max(bb.XMin - cx, 0, cx - bb.XMax)
    ny = max(bb.YMin - cy, 0, cy - bb.YMax)
    return math.hypot(nx, ny) <= r


for label, (path, inner_sign) in files.items():
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

    inner_edge_x = plate_bb.XMax if inner_sign > 0 else plate_bb.XMin
    thumb = [s.BoundBox for s in others if s.BoundBox.YMin < 10 and 500 < s.Volume < 2000]
    tcx = sum((b.XMin + b.XMax) / 2 for b in thumb) / len(thumb)
    tcy = sum((b.YMin + b.YMax) / 2 for b in thumb) / len(thumb)
    print(f"thumb centroid approx=({tcx:.1f},{tcy:.1f})  inner_edge_x={inner_edge_x:.2f}  "
          f"plate Y[{plate_bb.YMin:.1f},{plate_bb.YMax:.1f}]")

    x_lo = min(inner_edge_x, inner_edge_x - inner_sign * 50)
    x_hi = max(inner_edge_x, inner_edge_x - inner_sign * 50)
    x_lo = max(x_lo, plate_bb.XMin + OUTER_R + 1)
    x_hi = min(x_hi, plate_bb.XMax - OUTER_R - 1)
    y_lo = plate_bb.YMin + OUTER_R + 1
    y_hi = plate_bb.YMax - OUTER_R - 1

    found = []
    x = x_lo
    while x <= x_hi:
        y = y_lo
        while y <= y_hi:
            overlap = False
            for s in others:
                if bbox_maybe(s.BoundBox, x, y, OUTER_R):
                    probe = Part.makeCylinder(OUTER_R, HEIGHT, FreeCAD.Vector(x, y, 3.0))
                    if probe.common(s).Volume > 1.0:
                        overlap = True
                        break
            if not overlap:
                d = math.hypot(x - tcx, y - tcy)
                found.append((x, y, d))
            y += 5.0
        x += 5.0
        print(f"  x={x:.0f} scanned, {len(found)} valid so far", flush=True)

    found.sort(key=lambda t: t[2])
    print(f"Closest-to-thumb valid (no-socket-overlap) sites:")
    for x, y, d in found[:10]:
        print(f"  (x={x:.1f}, y={y:.1f}) dist_to_thumb_centroid={d:.1f}mm")

print("DONE", flush=True)
