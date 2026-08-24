"""Identify flat baseplate-register solids/faces and overall case envelope
in cosmotylleft.step / cosmotylright.step, using FreeCAD's Part module.

Run headlessly:
  & 'C:\\Program Files\\FreeCAD 1.1\\bin\\freecadcmd.exe' '_register_analysis.py'
"""
import FreeCAD, Part, math

files = {
    "LEFT": r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylleft.step",
    "RIGHT": r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylright.step",
}

Z = FreeCAD.Vector(0, 0, 1)
FLAT_TOL_DEG = 0.5

for label, path in files.items():
    print("=" * 78)
    print(f"{label}: {path}")
    print("=" * 78)
    shape = Part.Shape()
    shape.read(path)
    solids = shape.Solids
    print(f"Total solids: {len(solids)}")

    overall_bb = shape.BoundBox
    print(f"OVERALL bbox: X[{overall_bb.XMin:.2f},{overall_bb.XMax:.2f}] "
          f"Y[{overall_bb.YMin:.2f},{overall_bb.YMax:.2f}] "
          f"Z[{overall_bb.ZMin:.2f},{overall_bb.ZMax:.2f}]  "
          f"(W={overall_bb.XLength:.2f} D={overall_bb.YLength:.2f} H={overall_bb.ZLength:.2f})")

    flat_records = []  # (solid_idx, face_area, face_bbox, solid_bbox, solid_volume)
    key_socket_bbs = []  # per-key tilted-socket solids for later collision checks

    for i, solid in enumerate(solids):
        bb = solid.BoundBox
        vol = solid.Volume
        has_flat_register = False
        for f in solid.Faces:
            surf = f.Surface
            if surf.__class__.__name__ != "Plane":
                continue
            n = FreeCAD.Vector(surf.Axis.x, surf.Axis.y, surf.Axis.z)
            n.normalize()
            dot = max(-1.0, min(1.0, abs(n.dot(Z))))
            angle = math.degrees(math.acos(dot))
            if angle <= FLAT_TOL_DEG:
                fbb = f.BoundBox
                flat_records.append((i, f.Area, fbb, bb, vol))
                has_flat_register = True
        if not has_flat_register:
            key_socket_bbs.append((i, bb, vol))

    print(f"\nSolids containing a level (<= {FLAT_TOL_DEG} deg) planar face: "
          f"{len(set(r[0] for r in flat_records))} of {len(solids)}")
    print(f"Solids with NO level face (per-key sockets etc.): {len(key_socket_bbs)}")

    print("\n--- FLAT/LEVEL FACE RECORDS (candidate register surfaces) ---")
    for i, area, fbb, sbb, vol in flat_records:
        print(f"solid#{i:3d} vol={vol:9.1f}mm3  face_area={area:8.2f}mm^2  "
              f"face_bbox X[{fbb.XMin:7.2f},{fbb.XMax:7.2f}] Y[{fbb.YMin:7.2f},{fbb.YMax:7.2f}] "
              f"Z[{fbb.ZMin:6.2f},{fbb.ZMax:6.2f}]  "
              f"solid_bbox X[{sbb.XMin:7.2f},{sbb.XMax:7.2f}] Y[{sbb.YMin:7.2f},{sbb.YMax:7.2f}] "
              f"Z[{sbb.ZMin:6.2f},{sbb.ZMax:6.2f}]")

    # cylindrical sub-features (potential screw posts/pins) on flat-register solids
    print("\n--- CYLINDRICAL FACES on flat-register solids (candidate posts/pins/holes) ---")
    flat_solid_idxs = sorted(set(r[0] for r in flat_records))
    for i in flat_solid_idxs:
        solid = solids[i]
        for f in solid.Faces:
            surf = f.Surface
            if surf.__class__.__name__ == "Cylinder":
                fbb = f.BoundBox
                radius = surf.Radius
                axis = surf.Axis
                print(f"  solid#{i:3d} cylinder r={radius:6.3f}mm axis=({axis.x:.2f},{axis.y:.2f},{axis.z:.2f}) "
                      f"bbox X[{fbb.XMin:7.2f},{fbb.XMax:7.2f}] Y[{fbb.YMin:7.2f},{fbb.YMax:7.2f}] "
                      f"Z[{fbb.ZMin:6.2f},{fbb.ZMax:6.2f}]")

    # Envelope of all "no flat face" solids = per-key socket cluster envelope
    if key_socket_bbs:
        kx0 = min(b.XMin for _, b, _ in key_socket_bbs)
        kx1 = max(b.XMax for _, b, _ in key_socket_bbs)
        ky0 = min(b.YMin for _, b, _ in key_socket_bbs)
        ky1 = max(b.YMax for _, b, _ in key_socket_bbs)
        kz0 = min(b.ZMin for _, b, _ in key_socket_bbs)
        kz1 = max(b.ZMax for _, b, _ in key_socket_bbs)
        print(f"\nPer-key-socket solids envelope: X[{kx0:.2f},{kx1:.2f}] Y[{ky0:.2f},{ky1:.2f}] Z[{kz0:.2f},{kz1:.2f}]")

    print(f"\n--- ALL KEY-SOCKET SOLID BBOXES ({label}) ---")
    for i, bb, vol in key_socket_bbs:
        print(f"solid#{i:3d} vol={vol:8.1f}mm3 bbox X[{bb.XMin:7.2f},{bb.XMax:7.2f}] "
              f"Y[{bb.YMin:7.2f},{bb.YMax:7.2f}] Z[{bb.ZMin:6.2f},{bb.ZMax:6.2f}]")

print("\nDONE")
