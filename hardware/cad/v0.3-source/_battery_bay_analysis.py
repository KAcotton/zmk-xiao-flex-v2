"""Locate thumb-cluster key sockets, main case shell, and available in-case
vertical clearance for a vertical 18650 battery bay near the inner/thick
(most-tented) edge of each half.

Read-only analysis; writes nothing. Run headlessly:
  & 'C:\\Program Files\\FreeCAD 1.1\\bin\\freecadcmd.exe' '_battery_bay_analysis.py'
"""
import FreeCAD, Part, math

files = {
    "LEFT": (r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylleft.step", +1),
    "RIGHT": (r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylright.step", -1),
}

CELL_DIA = 18.6
CELL_LEN = 65.5
PROBE_MARGIN = 1.0  # mm radius slop for the clearance probe

for label, (path, inner_sign) in files.items():
    print("=" * 78)
    print(f"{label}  inner_sign={inner_sign}")
    shape = Part.Shape()
    shape.read(path)
    solids = shape.Solids
    print(f"Total solids: {len(solids)}")

    # Identify plate (flat Z=0 face > 10000mm^2) same as build_v03.py
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
    print(f"Plate bbox X[{plate_bb.XMin:.2f},{plate_bb.XMax:.2f}] Y[{plate_bb.YMin:.2f},{plate_bb.YMax:.2f}]")

    # No-flat-face solids = per-key sockets + sensor mount + main shell (mixed in)
    no_flat = []
    for i, s in enumerate(solids):
        if s is plate:
            continue
        has_flat = False
        for f in s.Faces:
            surf = f.Surface
            if surf.__class__.__name__ == "Plane":
                n = FreeCAD.Vector(surf.Axis.x, surf.Axis.y, surf.Axis.z)
                n.normalize()
                if abs(n.z) > 0.999 and abs(f.BoundBox.ZMin) < 0.5:
                    has_flat = True
        if not has_flat:
            no_flat.append((i, s))

    # main shell = largest-volume solid among the "no flat register" set
    no_flat.sort(key=lambda t: -t[1].Volume)
    shell_idx, shell = no_flat[0]
    print(f"\nMain case shell candidate: solid#{shell_idx} vol={shell.Volume:.0f}mm3 "
          f"bbox X[{shell.BoundBox.XMin:.2f},{shell.BoundBox.XMax:.2f}] "
          f"Y[{shell.BoundBox.YMin:.2f},{shell.BoundBox.YMax:.2f}] "
          f"Z[{shell.BoundBox.ZMin:.2f},{shell.BoundBox.ZMax:.2f}]")

    others = no_flat[1:]  # per-key sockets, sensor mount, misc small parts
    print(f"\nRemaining {len(others)} 'no flat face, not shell' solids "
          f"(key sockets / sensor mount / misc), sorted by X (toward inner edge "
          f"{'max' if inner_sign > 0 else 'min'}):")
    others_sorted = sorted(others, key=lambda t: inner_sign * t[1].BoundBox.XMin, reverse=True)
    for i, s in others_sorted:
        bb = s.BoundBox
        cx = (bb.XMin + bb.XMax) / 2.0
        cy = (bb.YMin + bb.YMax) / 2.0
        print(f"  solid#{i:3d} vol={s.Volume:8.1f}mm3 centroid=({cx:7.2f},{cy:7.2f}) "
              f"bbox X[{bb.XMin:7.2f},{bb.XMax:7.2f}] Y[{bb.YMin:7.2f},{bb.YMax:7.2f}] "
              f"Z[{bb.ZMin:6.2f},{bb.ZMax:6.2f}]")

    inner_edge_x = plate_bb.XMax if inner_sign > 0 else plate_bb.XMin
    print(f"\ninner_edge_x = {inner_edge_x:.2f}")

print("\nDONE")
