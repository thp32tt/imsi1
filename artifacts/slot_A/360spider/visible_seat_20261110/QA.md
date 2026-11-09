# Ferrari 360 Spider / SLOT A / native visible-seat first-pass geometry

Status: COVERED_PARTIAL_QA. Whole-car QA NOT PASS. One actual native geometry edit.

- Native original PMT SHA256: a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6. Kept on N100 only.
- Original imported editable Blender SHA256: b4f1d071119693172bbf786809da62dce8acb0c84e52d9779a6b1a996654ce57.
- Accepted input center console Blender SHA256: 5dabffb52ae4136b6b72f99c7975b629820f839afec2048e59035cb74d8ee612.
- Editable output seat Blender SHA256: af5a9a9d9650d261b1b24f56e5ff8b5291773e033c43087e000276940fbc87a2.
- Original mesh PMT_object00_group01_material010_a0: 20 existing native seat vertices changed. Local seat backrest toward occupants up to 38 mm, seat bolsters up to 18 mm, front seat-cushion lift up to 30 mm, both left and right seat sides. No added objects or faces. Original UV/normals/topology preserved.
- Previous accepted center-console vertices unchanged. Other 74 native meshes unchanged, windshield/front-glass/frame/A-pillars and adjoining seals unchanged.
- Authentic photo reference: private N100 360 Spider interior 01_interior.jpg; broad seat/bolster profile only. No exact photo registration or game-driver-eye equivalence claimed.
- Blender 4.5.15 independent clean reopen native geometry/UV/normal/75-mesh fingerprint PASS. workspace_guard.py verify-receipt PASS.
- No synthetic mesh, textures, exterior/wheel edits, OVC/OVC3/PMT export, game integration, Model2 or Dino.
- Matched BEFORE/AFTER camera comparison: comparison_seat_before_after.jpg; before/after oblique and top PNG evidence.
- Next target instrument_cluster (0/2). 24h vehicle assignment stays. Full vehicle photo/camera quality gate pending.