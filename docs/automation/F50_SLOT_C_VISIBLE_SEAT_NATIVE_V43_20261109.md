# Ferrari F50 SLOT C — visible_seat v43 (2026-11-09 KST)

- **Status:** `COVERED_PARTIAL_QA`, not a vehicle-wide QA PASS. Slot C stays F50 throughout 24-hour assignment; next component `instrument_cluster`, 0/2 dispatches.
- **Repository:** `thp32tt/imsi1@main`; plaintext editable source checkpoint, no encryption, Secret, or transformation to PMT/OVC/OVC3/game.
- **Original source:** N100 original OutRun 2006 `obj_plcar_f50_pmt.sz` SHA256 `10daa1312b6cff0267b38b4c440c6007c68b470a225ca15f0c324876fd80aeab`. Raw original package is **not** published. Native original import `.blend` SHA256 `d82b3d024a812126da5b38c56572cfc326fbe3d1b5c0ddf8cad4cbd855119d31`.
- **Accepted input:** restored original-derived v40 `F50_OriginalPMT_InnerDoor_UpperRail_v40.blend` SHA256 `03b96b1eb2293c151c60133919380055fa8393372b0acbf18045edf25faa949a`. Rejected windshield v41 is **not** an ancestor of this edit.
- **Native PMT target:** `object00_group01_material023_a0` (Blender object `PMT_F50_object00_group01_material023_a0`); two mirrored source 64-vertex seat-shell components, physically inspected as bucket-seat frame with the isolated original-source Blender render.
- **Actual geometry edit:** 118 original vertices moved; shoulder contour, side-bolster envelope, mid-back support sculpted from source mesh; max displacement 0.0232682m. No new seat object, added mesh, polygons, material, texture, PBR, OVC, OVC3, game export or installation.
- **Isolation proof:** all 41 other original source mesh object coordinate/topology/transform fingerprints stayed unchanged, including dashboard/steering/windshield/glass/A-pillars/exterior. Within the target object, non-seat connected components were not edited.
- **Photo reference:** N100 private `outrun2_vr_refs/20261104_16car_cockpit/03_F50/REF5_mecum_interior_02_552c4a048.jpg`. Original photo remains on N100. Black bucket frame and side bolsters compared qualitatively only; original game eye camera and seven-view alignment are not calibrated.
- **Output:** `F50_OriginalPMT_VisibleSeat_Bolster_v43.blend` SHA256 `a1f64d8f2f7e540978cfb9ae41c58dde2732f6a83c0a537c8860dee09f3768c7`. Blender 4.5.15 LTS real save + separate-process fresh reopen **PASS**; reassembled six plaintext 256KiB max parts with `reassemble.py --verify-only` **PASS**.
- **Comparison render:** source 023 isolated matched workbench BEFORE/AFTER, 105649 changed RGB pixels (threshold >3). This is a geometry isolation preview, not proof of full in-game photo fidelity.
- **Boundary:** user-protected windshield and glass-adjacent region must never be edited. No dashboard or wheel micro-adjustments.
- **Next:** `instrument_cluster`. Mark any unidentified original cluster region `BLOCKED` rather than constructing a surrogate; maintain 2-dispatch max per component and 24-hour vehicle window. Full vehicle QA remains **NOT PASS**.

## Plaintext artifact paths

`artifacts/slot_C/f50/visible_seat_v43/manifest.json` contains native, input, output, part SHA256s, sizes and source proof. Use adjacent `reassemble.py` to recreate the editable .blend and check SHA256. Source authoring scripts are under `tools/car_modeling/slot_c/`.
