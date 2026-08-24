# v0.2 modular baseplate — OpenSCAD sources

Corrects v0.1, which modeled the new baseplate as a flat rectangular box
sized to the STL bounding box. The real case is an organic, sculpted,
per-column shape (see `Misc/CASES.webp`). Full writeup:
[../../design-notes/v0.2-baseplate-tenting-battery.md](../../design-notes/v0.2-baseplate-tenting-battery.md) —
read that first, this README only covers how to render these files.

## How this works

- `lib/organic_outline.scad` — `projection()`s the REAL `21.05.01 CASE
LEFT.stl` / `21.05.02 CASE RIGHT.stl` meshes down to a 2D silhouette.
  `projection()` works even though those CASE meshes are **not closed**
  (confirmed: OpenSCAD refuses 3D boolean CSG against them — see design
  notes), because it doesn't require a manifold solid.
- `lib/organic_tray.scad` — extrudes that real 2D outline into an open-top
  tray (floor + wall ring), then adds/subtracts ordinary primitives
  (battery pocket capsule, corner posts, controller standoffs) — all safe
  CSG since none of it operates on the mesh itself.
- `baseplate_left.scad` / `baseplate_right.scad` — per-half printable trays.
  **Must stay directly in this folder** — `import()` paths in
  `lib/organic_outline.scad` are one level up (`../21.05.01 CASE LEFT.stl`
  etc.), resolved relative to the top-level rendered file's directory, not
  `lib/`'s.
- `fit_check_left.scad` / `fit_check_right.scad` — preview-only (`%`)
  overlay of the real CASE + PLATE solids against the new tray, for visual
  alignment checks in the OpenSCAD GUI (F5). Do not F6/CGAL-render these.

## Rendering

```
& "C:\Program Files\OpenSCAD\openscad.exe" -o baseplate_left.stl  hardware\cad\v0.2\baseplate_left.scad
& "C:\Program Files\OpenSCAD\openscad.exe" -o baseplate_right.stl hardware\cad\v0.2\baseplate_right.scad
```

Both were test-rendered successfully in this pass (no CGAL/manifold errors,
valid closed solids produced). That confirms the _pipeline_ works — it does
**not** confirm the design is correct/print-ready. See design notes for what
is still unverified (battery pocket clearance, corner post positions,
flat-vs-contoured mating face).
