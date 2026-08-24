// TylerDactyl v0.2 — real-mesh outline helpers.
//
// projection() flattens the actual imported mesh triangles to a 2D
// silhouette. Unlike full 3D boolean CSG (difference/union/intersection,
// which route through CGAL_Nef_Polyhedron and REQUIRE a closed/manifold
// mesh), projection() works directly off the raw triangle soup and does
// NOT require a closed mesh. This matters here: the CASE STLs are
// confirmed NOT closed (OpenSCAD: "The given mesh is not closed! Unable to
// convert to CGAL_Nef_Polyhedron."), so 3D booleans against them fail, but
// their projection() outline still renders correctly and quickly (~2s).
//
// This is the reason v0.2 builds the new baseplate from 2D outlines
// (extruded) instead of doing direct 3D booleans against the CASE mesh.

// side: "left" | "right"
// NOTE: OpenSCAD resolves import() relative paths against the top-level
// rendered/entry file's directory (e.g. v0.2/baseplate_left.scad), NOT the
// directory of this included library file (v0.2/lib/) — so these paths
// only go up one level (v0.2/ -> hardware/cad/), not two. Entry files must
// live directly in hardware/cad/v0.2/ for this to resolve correctly.
module plate_outline(side) {
    file = side == "left" ? "../21.05.04 PLATE LEFT.stl" : "../21.05.06 PLATE RIGHT.stl";
    projection(cut = false) import(file);
}

module case_outline(side) {
    file = side == "left" ? "../21.05.01 CASE LEFT.stl" : "../21.05.02 CASE RIGHT.stl";
    projection(cut = false) import(file);
}

// Full 3D reference import, for preview-only (%) overlays in fit-check
// files. Do NOT boolean against this — it will fail (non-manifold CASE
// meshes) or may silently misbehave (PLATE mesh IS closed/manifold and
// CAN be boolean'd, but is not used that way here — see design notes for
// why the CASE's real bottom-rim contour, not the flat PLATE, is what
// actually needs to be matched, and why that contour is not accessible via
// CSG in this pass).
module case_solid_preview(side) {
    file = side == "left" ? "../21.05.01 CASE LEFT.stl" : "../21.05.02 CASE RIGHT.stl";
    %import(file);
}

module plate_solid_preview(side) {
    file = side == "left" ? "../21.05.04 PLATE LEFT.stl" : "../21.05.06 PLATE RIGHT.stl";
    %import(file);
}
