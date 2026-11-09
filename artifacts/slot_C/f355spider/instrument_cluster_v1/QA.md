# F355 Spider / SLOT C / native instrument_cluster pass

- **Geometry:** only existing PMT `object00_group01_material016_a0` upper gauge-binnacle visor vertices, **40 moved**; max **34.12 mm**. No topology, object transform, material or texture change.
- **Unchanged:** 95 other PMT-derived native Blender meshes, the separate instrument gauge face PMT011, previous center console/seat, steering wheel, dashboard outside the target, windshield/glass/frame/A-pillar/borders and all exterior parts.
- **Source:** native N100 original PMT SHA256 `d9af341653ef44371e8df2efc4024af92d7ca03665acef04a4c3c65200bb7b11`, source baseline SHA256 `4fa9bdc314c5e30ab890adcff160377436540646588a36f1c4c1649c5df7186e`. No original PMT or private photograph uploaded.
- **Input .blend:** `6b179f9d275226ade32960ac49f52cec8149247dc43726f311cb79beeeb06802`. **Output .blend:** `ec320da62a7ac21bf88cef5ed205558f3542e03f6f35d6f76de5d4e3d7643e23`. Original 96 mesh identities retained.
- **Validation:** Blender 4.5.15 separate process save/reopen PASS, `workspace_guard verify-receipt` PASS, same-camera before/after and delta PNGs in this directory; source-native fingerprint receipt attached.
- **Reference:** N100 private LHD F355 Spider interior photo; gauge-cluster hood silhouette visually consulted, **not camera registered or dimensionally measured**. Gaming test, calibrated driver-eye and comprehensive cabin seam QA remain outstanding.
- **Gate:** `COVERED_PARTIAL_QA` for this part; full vehicle QA **NOT PASS**. Next part `dashboard` (fresh initial pass, no historical steering/dashboard micro-polish loops).