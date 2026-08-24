"""Find a valid (cx,cy) for the vertical battery turret's outer footprint:
near the inner (most-tented) edge, within the thumb-cluster Y-band, with
ZERO real 3D overlap against any key-socket/sensor-mount solid (shell
overlap is fine/expected -- that's the case-shell material we plan to cut
away for the turret).
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
EDGE_INSET = 2.0


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
                n = FreeCAD.Vector(surf.Surface.Axis.x if False else surf.Axis.x, surf.Axis.y, surf.Axis.z)
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
    cx = inner_edge_x - inner_sign * (OUTER_R + EDGE_INSET)

    thumb = [s.BoundBox for s in others if s.BoundBox.YMin < 10 and 500 < s.Volume < 2000]
    ty0 = min(b.YMin for b in thumb) - 5
    ty1 = max(b.YMax for b in thumb) + 5
    print(f"cx={cx:.2f} inner_edge_x={inner_edge_x:.2f}  thumb Y-band [{ty0:.1f},{ty1:.1f}]")

    found = []
    cy = ty0
    while cy <= ty1:
        overlap = False
        for s in others:
            if bbox_maybe(s.BoundBox, cx, cy, OUTER_R):
                probe = Part.makeCylinder(OUTER_R, HEIGHT, FreeCAD.Vector(cx, cy, 3.0))
                if probe.common(s).Volume > 1.0:
                    overlap = True
                    break
        if not overlap:
            found.append(cy)
        cy += 2.0

    print(f"Valid cy values (zero overlap vs sockets/sensor, shell overlap OK) within thumb band: {found}")

print("DONE", flush=True)
