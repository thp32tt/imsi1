# Ferrari 360 Spider / SLOT A / instrument_cluster R03
Status: **COVERED_PARTIAL_QA**, **NOT** vehicle QA PASS. Unique material geometry checkpoint, not doc-only.
- Original game PMT SHA256: `a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6` (remains N100).
- Native source import SHA256: `b4f1d071119693172bbf786809da62dce8acb0c84e52d9779a6b1a996654ce57`.
- Accepted input (seat R02) SHA256: `af5a9a9d9650d261b1b24f56e5ff8b5291773e033c43087e000276940fbc87a2`.
- Output Blender R03 SHA256: `df7b2ce23530c4bdace9d301cde61526d5ef5ab80ab7f9811f35d4dda08de443`.
- Existing PMT mesh: `PMT_object00_group01_material010_a0`, 20 existing vertices; native 5-island cluster face/hood only.
- Shape: existing gauge binnacle eyebrow +20 mm and instrument face recess up to 32 mm, no added gauge models, objects, vertices, faces, UV, textures or PBR.
- Fresh Blender 4.5.15 independent reopen PASS; original native mesh inventory 75; other 74 untouched. Previous seat/console vertex edits preserved.
- Protected windshield, A pillars, borders, seals, external/wheels unchanged.
- Same-camera original-derived ROI comparison render: `comparison_instrument_seated_before_after.jpg`. RGB pixels changed (>4): 52580. Render is proof of geometric appearance difference, not calibrated real-game QA.
- Private 360 Spider interior photo `04_360_Spider/01_interior.jpg` inspected as silhouette reference only (not uploaded). Exact driver-eye/photo registration remains outstanding.
- **Next component**: `dashboard` (new-car first pass only; no prior wheel or dash polish). Whole-car QA remains **NOT_PASS**.
