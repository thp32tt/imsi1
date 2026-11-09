# Ferrari 360 Spider — SLOT A cross-cockpit QA (2026-11-10)

**Status: QA_WAITING_INPUT; vehicle QA PASS: NO.**

## Actual integrated source evidence
Official Blender 4.5.15 reopened and compared original-native R00 to accepted R01 console, R02 visible seat, R03 instrument binnacle and R04 dashboard source .blend snapshots. Original PMT SHA256: `a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6`. Each of five .blend SHA256 values matches existing workpack/manifest. R04 SHA256: `403ec48d0e9761214f20a5c22a7df608f38b3644b135b80aa185dcb559c33ad8`.

Read-only whole-scene invariant audit: **PASS**. All 75 native PMT object IDs retained, 12,424 original vertices, all face/edge topology and transforms unchanged. Only `PMT_object00_group01_material010_a0` changed, in 16 (console) + 20 (seat) + 20 (instrument) + 6 (dashboard) mutually disjoint, previously edited native vertices. All **62** cumulative changes retained in R04; 74 other native PMT meshes (including protected windshield-associated non-target meshes) identical. No newly generated mesh, Blender scene, texture, conversion, or game export. Existing steering, door and controls blockers are not overridden.

## Final vehicle gate not met
`04_360_Spider` N100 original real-vehicle photographs exist; the reference catalog's exact LHD driver-eye / seven matched individual cockpit views are **not certified**. Original-game seated camera has **not** been calibrated to authentic photographs. No reliable pixel-space photographic silhouette verdict can be issued; the geometry coherence PASS does not imply photo QA or whole-car PASS.

QA is recorded **once** as `QA_WAITING_INPUT` without consuming a source-edit dispatch or changing cars. Do not rerun the same-input QA, polish dashboard/steering, or promote the vehicle without calibrated original-game eye and authenticated same-camera reference views.

Blender test script: `tools/car_modeling/audit_360spider_cross_cockpit.py`; machine-readable evidence: `artifacts/slot_A/360spider/cross_cockpit_qa_20261110/geometry_audit.json`. Photos and original PMT remain N100-only.
