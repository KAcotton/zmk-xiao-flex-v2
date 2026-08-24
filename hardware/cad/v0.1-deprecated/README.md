# v0.1 modular baseplate — OpenSCAD sources

Parametric, text-based CAD for the tenting/battery baseplate redesign. See the
full design writeup in
[../../design-notes/v0.1-baseplate-tenting-battery.md](../../design-notes/v0.1-baseplate-tenting-battery.md)
for the mechanism rationale, assumptions, and open questions — read that
first, this README only covers how to render these files.

**Status: authored but not yet rendered.** No OpenSCAD install was available
in the environment that generated these files, so none of this has been
opened in OpenSCAD, checked for a valid manifold solid, or exported to STL.
Treat it as a careful first draft, not a print-ready output.

## Files

- `lib/params.scad` — shared dimensions (footprints, cell/holder, controller,
  fastener sizes). Edit this first when adjusting the design.
- `lib/baseplate_tray.scad` — shared tray module (battery bay, controller
  shelf, corner posts, switch/flex-cable cutouts) used by both halves.
- `baseplate_left.scad` / `baseplate_right.scad` — per-half printable trays.
- `tenting_shim_set.scad` — the 4-block interchangeable tenting shim set.
  Edit `TENT_ANGLE_DEG` (or pass `-D TENT_ANGLE_DEG=16`) to generate a
  different angle; re-run per desired angle in `TENT_ANGLES`.
- `fit_check_left.scad` / `fit_check_right.scad` — overlays the new tray
  against the real existing CASE/PLATE STLs for a translucent visual
  footprint check. Preview only (uses `%`), not exportable geometry.

## Rendering

```
openscad hardware/cad/v0.1/baseplate_left.scad
openscad -o hardware/cad/v0.1/out/baseplate_left.stl hardware/cad/v0.1/baseplate_left.scad
openscad -D TENT_ANGLE_DEG=16 -o hardware/cad/v0.1/out/tent_16deg_left.stl hardware/cad/v0.1/tenting_shim_set.scad
```

Before printing anything: open each file in the OpenSCAD GUI, confirm
"Render" (F6) succeeds with no CGAL/manifold warnings, and cross-check
against the open questions in the design notes doc.
