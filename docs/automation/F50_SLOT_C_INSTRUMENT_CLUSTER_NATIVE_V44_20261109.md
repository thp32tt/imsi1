# F50 SLOT C — native PMT011 instrument cluster v44 (2026-11-09 KST)

**Status: COVERED_PARTIAL_QA, not whole-car QA PASS.** `FERRARI16-SLOTC-F50-PMT011-INSTRUMENT-CLUSTER-V44-20261109`

This checkpoint changes the existing original OutRun 2006 F50 instrument-hood mesh only. The actual source mesh `PMT_F50_object00_group01_material011_a0` contains **109 existing vertices / 119 faces**. **40 existing vertices** of the black instrument-cluster brow were moved (maximum 12.5953 mm); object count, mesh face count and all **41 other original PMT meshes** are geometrically unchanged. No new mesh/object, synthetic gauge dials, texture, PBR, glass edits, dashboard/steering refinements or game export.

## Provenance and local real Blender validation

- Original native source, retained on N100: `obj_plcar_f50_pmt.sz` SHA256 `10daa1312b6cff0267b38b4c440c6007c68b470a225ca15f0c324876fd80aeab`.
- Original imported source `.blend` SHA256 `d82b3d024a812126da5b38c56572cfc326fbe3d1b5c0ddf8cad4cbd855119d31`.
- Accepted source-derived v43 input `.blend` SHA256 `a1f64d8f2f7e540978cfb9ae41c58dde2732f6a83c0a537c8860dee09f3768c7`.
- New **editable v44 `.blend`** SHA256 `1ff620c4ede9a265b66440105c16cd318f4e9e3761ec2754d13866f0b7d7507e`.
- Official Blender 4.5.15 LTS: actual source edit + Workbench matched-camera BEFORE/AFTER rendering + separate-process v44 load and exact source-mesh fingerprint inventory check **PASS**.
- `workspace_guard.py verify-receipt --slot C`: **PASS**, modified original source object count 1, non-target native mesh count 41 unchanged.
- Private authentic comparison photo kept on N100: `03_F50/REF2_dashboard_closeup_dad64db8c0a5.jpg`. The F50 photo has a low black rounded instrument brow; the existing crown/return strip received a tapered local lift. Camera and seven-photo fidelity are **not calibrated or certified**.
- Matched comparison image SHA256 `951c8d916bc29928479bfa35b95dc5eb15c4770ddae993eae2d5082f69bcbab0`.

## Plaintext public work product

`artifacts/slot_C/f50/instrument_cluster_v44/` holds an **unencrypted editable `.blend`** (and SHA256-verifiable plaintext `partNN.bin` slices), `manifest.json`, `reassemble.py`, `receipt.json`, matched BEFORE/AFTER renders and comparison. Source script: `tools/car_modeling/slot_c/f50_instrument_cluster_v44.py`. The raw PMT package and source photo files are not published.

## Gate and next dispatch

`instrument_cluster` is **COVERED_PARTIAL_QA (1/2 used)**, so do not rework this merely to consume another turn. Next in component order is `dashboard`, currently **P0_POLISH_HOLD**; no dashboard or steering re-polish without explicit new defect ID and guard authorization. If unblocked edits are unavailable, proceed to independent `cross_cockpit_qa` observation instead of fabricated geometry. Slot C remains **F50**; original 24-hour ownership and full seven-view, driver-eye and real-geometry QA acceptance gates remain unchanged.