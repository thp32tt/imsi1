# SLOT A — Daytona original PMT017 seat R46 (2026-11-09)

- **Result:** `COVERED_PARTIAL_QA`, **NOT full-car QA PASS**; next `instrument_cluster`.
- **Only original-game mesh edited:** `object00_group01_material017_a0` (184 source vertices / 300 source faces; two authentic native seat components of 94/90 vertices). This is NOT a generated/approximate replacement.
- **New geometry:** original PMT vertices actually moved **82** (left 42, right 40); cushion side support 58 and upper seatback side roll 24; max displacement **12.5 mm**. No new geometry, materials, textures, faces or topology.
- **No change to** the other 30 original-import meshes, dashboard/steering, glass/windshield/A-pillars, Dino or F50; no game export.
- **Native PMT** SHA256 `f393ba5c706453a4d3f71604f25cd1631594152380856462fb0a504143ba6abe` remains solely N100.
- **Input** original-import editable scene SHA256 `92c82ee5c4e0631195cb314e0d8e2f56a78a6a58da3c809c46b1da0f9d2c71a3`.
- **Output** independent source-native seat Blender SHA256 `e84c723111f8409686ee2d4e953c021212a76055bcb24ba0aad8138ebae828a4`.
- **Important limitation:** accepted *integrated* R45 scene SHA256 `224131c7adc928d5d6f0377d030d5a350c59b8664c13303a2731d6dfc6e9a722` remains unchanged; this seat-only native Blender is NOT merged into R45, not a drop-in game or whole-cockpit update. Prior R45 V5/V8 high-density seat descendants lack byte-exact native-vertex attribution and were NOT edited.
- **Reopen** `PASS_INDEPENDENT_BLENDER_4_5_15_SAVE_REOPEN` in Blender 4.5.15 LTS, 30 unchanged mesh signatures confirmed.
- **Real reference photos compared locally:** `REF5_mecum_interior_05_464b30a6d.jpg` (seat/profile), `REF5_mecum_interior_02_cb27ab7aa.jpg` (pad/bolster detail), kept N100 only. Comparison render is actual same-camera original vs R46, NOT the private photos.
- **Render** `Daytona365_NATIVE_PMT017_R45Ref_R46_BeforeAfter.png` at matching workbench camera, RGB>3 pixels changed: 55026.
- **Pending QA:** true original-game eye calibration, 7-view reference coverage, potential future source-native integration into accepted R45. Do not promote car QA PASS.
- **Delivery:** editable plain .blend + Python and QA files in temporary public imsi1; no encryption/Secret/reassembly because single .blend is <1.4 MB.