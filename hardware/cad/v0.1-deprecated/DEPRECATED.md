# DEPRECATED — do not use

This v0.1 baseplate (`baseplate_left.scad` / `baseplate_right.scad` and
`lib/baseplate_tray.scad`) modeled the new baseplate as a **flat rectangular
box sized to the STL bounding box** of each case half. That is wrong: the
real TylerDactyl case is a sculpted, organic, per-finger-column stepped
surface (see `Misc/CASES.webp` and the actual CASE/PLATE STLs) — not a flat
rectangular tray. The user rejected this pass as not matching the real
footprint.

Superseded by [../v0.2/](../v0.2/) and
[../../design-notes/v0.2-baseplate-tenting-battery.md](../../design-notes/v0.2-baseplate-tenting-battery.md).
Kept here for history only; do not render, print, or build on top of these
files.
