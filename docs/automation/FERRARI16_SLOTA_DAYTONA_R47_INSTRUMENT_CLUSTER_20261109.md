# SLOT A — Daytona original PMT015 instrument cluster R47

- Status: **COVERED_PARTIAL_QA**, **NOT full vehicle QA PASS**. Next part: `dashboard` (P0 polish hold; do not automatically edit without explicit defect).
- Real original native PMT: `obj_plcar_dayts_pmt.sz` (N100 only), SHA256 `f393ba5c706453a4d3f71604f25cd1631594152380856462fb0a504143ba6abe`.
- Native original import .blend (N100): SHA256 `92c82ee5c4e0631195cb314e0d8e2f56a78a6a58da3c809c46b1da0f9d2c71a3`.
- Sole modified mesh: `object00_group01_material015_a0`, actual **20 existing native PMT vertices** in two gauge-bezel strip connected components (anchors 229/253), front lip moved toward the driver by up to **7.5 mm**. Same vertices/faces, original UVs/materials retained.
- Other **29 native original meshes unchanged**, including gauge face PMT014, windshield, A-pillars, dashboard body and steering wheel.
- Output independent editable Blender `artifacts/slot_A/daytona365/R47_instrument_cluster/Daytona365_NATIVE_PMT015_InstrumentCluster_R47.blend` SHA256 `7367034bf9900e380f0f61d8d89c19322e8d22207dcba6c5124bf8f572803c28`. Blender 4.5.15 actual save, separate-process reopen/fingerprint audit and `workspace_guard.py verify-receipt` **PASS**.
- Local photo comparison used only authentic 365 GTS/4 gauge panel close-up `REF11_steering_instrument_closeup_5769d1ef1b.jpg` and original dash interior `REF2_dashboard_original_e91527ff82f3.jpg`; these source images remain private on N100 (not included here).
- Actual before/after same-camera Blender Workbench: `Daytona365_NATIVE_PMT015_R47_BeforeAfter.png`; pixel changes RGB>3: **13120**. This is not an original-game camera or complete photo QA.
- Earlier accepted integrated R45 scene SHA256 `224131c7adc928d5d6f0377d030d5a350c59b8664c13303a2731d6dfc6e9a722` **unchanged**. R46 seat and R47 gauge edits are standalone original-native proofs, **not merged** into R45 and not installable game replacements.
- No PMT/OVC/OVC3 export, external wheel/body, new materials, PBR, textures, game integration or Dino/Model2 changes. No AES, Secrets or encrypted assets.
- Outstanding vehicle gate: calibrated actual driver-eye viewpoint, seven authenticated photo views, source mesh connectivity QA and standalone native-to-integrated scene QA.