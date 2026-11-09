# 360 Spider SLOT A — original PMT dashboard R04

**Scope:** `dashboard` only. **Result:** `COVERED_PARTIAL_QA` (not full-car QA PASS).

- GitHub SSOT at entry: `main@354a10498b8595d1d033d732cc1543113c19aaef`, `active_by_slot.A=360spider`, workpack `current_component=dashboard`, first dispatch (0/2 previously consumed).
- Original game PMT SHA256: `a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6`; original Blender baseline SHA256: `b4f1d071119693172bbf786809da62dce8acb0c84e52d9779a6b1a996654ce57`.
- Accepted input R03 SHA256: `df7b2ce23530c4bdace9d301cde61526d5ef5ab80ab7f9811f35d4dda08de443`.
- New independent editable R04 .blend SHA256: `403ec48d0e9761214f20a5c22a7df608f38b3644b135b80aa185dcb559c33ad8`.
- Original native PMT mesh `PMT_object00_group01_material010_a0`, existing vertices `[1501, 1504, 1509, 1550, 1554, 1555]`. Three split-seam pairs, geometric displacement up 18/22/33 mm on **passenger-side interior dashboard rear contour** (0.79m span); no additional mesh, topology, transform, UV or material edits.
- Other 74 native PMT meshes geometrically unchanged. All vertices not in six-index allowlist unchanged, including source-native instrument cluster, seat, console, windshield glass, A-pillars and glass-boundary seams.
- Blender 4.5.15 independent new-process save/reopen + per-object geometry fingerprint & per-index delta: **PASS**.
- Real Ferrari 360 Spider private interior photograph reviewed on N100. Target contour chosen from source-native mesh, but camera/metric registration not validated. Photo **not uploaded**.
- Same-camera before/after isolated source mesh render: `dashboard_compare_seated.jpg`, `dashboard_compare_overhead.jpg`. Camera only QA, not saved in editable deliverable.
- Source package remains N100, and no OVC, OVC3, PMT export, textures, PBR, glass geometry, car exterior, game integration or synthetic car mesh was created.
- Next region in same A car: `steering_wheel`. This operation **did not edit** steering/wheel and did not mark any vehicle gate PASS.
