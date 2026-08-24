import FreeCAD, Part, math

files = {
    "LEFT": r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylleft.step",
    "RIGHT": r"c:\Users\tylerj\Documents\PERSONAL\KEYBOARD\zmk-xiao-flex-v2\hardware\cad\v0.3-source\cosmotylright.step",
}

Z = FreeCAD.Vector(0, 0, 1)

for label, path in files.items():
    print("=" * 70)
    print(f"{label}: {path}")
    print("=" * 70)
    shape = Part.Shape()
    shape.read(path)
    solids = shape.Solids
    print(f"Total solids: {len(solids)}")
    if not solids:
        print("No solids found; falling back to top-level Shells/Faces")
        solids = shape.Shells or [shape]

    for i, solid in enumerate(solids):
        bb = solid.BoundBox
        print(f"\n--- Solid {i} ---")
        print(f"Faces: {len(solid.Faces)}")
        print(f"BoundBox min: ({bb.XMin:.3f}, {bb.YMin:.3f}, {bb.ZMin:.3f})")
        print(f"BoundBox max: ({bb.XMax:.3f}, {bb.YMax:.3f}, {bb.ZMax:.3f})")
        print(f"Dimensions (W,D,H): ({bb.XLength:.3f}, {bb.YLength:.3f}, {bb.ZLength:.3f})")

        planar_faces = []
        for f in solid.Faces:
            surf = f.Surface
            if surf.__class__.__name__ == "Plane":
                normal = surf.Axis
                # normalize
                n = FreeCAD.Vector(normal.x, normal.y, normal.z)
                n.normalize()
                area = f.Area
                planar_faces.append((area, n, f))

        planar_faces.sort(key=lambda x: -x[0])
        print(f"Planar faces found: {len(planar_faces)}")
        for area, n, f in planar_faces[:5]:
            dot = max(-1.0, min(1.0, n.dot(Z)))
            angle = math.degrees(math.acos(abs(dot)))
            fbb = f.BoundBox
            print(f"  area={area:9.2f}mm^2  normal=({n.x:.4f},{n.y:.4f},{n.z:.4f})  "
                  f"angle_to_Z={angle:6.2f}deg  z_range=({fbb.ZMin:.2f},{fbb.ZMax:.2f})")

print("\nDONE")
