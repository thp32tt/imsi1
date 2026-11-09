# Ferrari F50 · SLOT C · dashboard dispatch guard · 2026-11-09 14:01 KST

- **Result:** `BLOCKED_OUT_OF_ORDER_P0_POLISH_HOLD`. Not a new geometry achievement, not vehicle QA PASS.
- **SSOT checked:** `thp32tt/imsi1@main` at `7678041dcd19ed23aa92d9127b8a692b04281d30`. `active_by_slot.C=f50`.
- **Persisted task:** `current_component=cross_cockpit_qa`, `dispatches_on_component=0`; dashboard and steering are `P0_POLISH_HOLD`.
- **Reason:** Dashboard/steering have already undergone extensive P0 iterations; no named new dashboard defect authorizes another edit. Dispatch budget is not reset. Do **not** edit dashboard/wheel, skip guard, or create a fake new model. Proceed to read-only `cross_cockpit_qa`.
- **Native F50 PMT:** N100 original file `rea-input/outrun/outrun2006/Cars/obj_plcar_f50_pmt.sz`, independently rehashed in this dispatch: SHA256 `10daa1312b6cff0267b38b4c440c6007c68b470a225ca15f0c324876fd80aeab`.
- **Original imported Blender scene SHA256:** `d82b3d024a812126da5b38c56572cfc326fbe3d1b5c0ddf8cad4cbd855119d31`.
- **Accepted editable input:** `artifacts/slot_C/f50/instrument_cluster_v44/F50_OriginalPMT_InstrumentCluster_v44.blend`, SHA256 `1ff620c4ede9a265b66440105c16cd318f4e9e3761ec2754d13866f0b7d7507e` per v44 manifest. **Unchanged output SHA:** same digest. No new .blend, geometry, Blender save/reopen or render is claimed for this dispatch.
- **Private photo observation (N100 only):** `REF2_dashboard_closeup_dad64db8c0a5.jpg` (SHA256 `6d2a66553b22fbf03f9bfdceed2a9bc5930cc0564da8b8bbe7a45bb01f6d8961`) shows arched gauge hood, padded upper dash, contrasting lower fascia and circular air vents. `REF5_mecum_interior_01_f8afa7e2a.jpg` (SHA256 `cd31303113763596eebada76ea964386522f4a03c9684c9132226963e8663ca2`) provides the wider cabin context. These are reference-only visual observations; a calibrated v44 driver-eye matched-angle comparison has **not** been made and no fit claim is warranted.
- **Outstanding blockers:** native source attribution for stalk/pedals and shifter gate/tunnel, final seven-view comparison, exact driver-eye calibration, existing geometry QA. Protected windshield/glass frame/A-pillars untouched. No exported PMT/OVC/OVC3, new textures/PBR, game integration, secrets or encryption.
- **Next:** `cross_cockpit_qa` observation-only, then specific user-authorized defect remediation if gated. Keep F50 assigned, do not advance to another car.
- **Evidence manifest:** `artifacts/slot_C/f50/dashboard_dispatch_blocked_20261109_1401/manifest.json`.
