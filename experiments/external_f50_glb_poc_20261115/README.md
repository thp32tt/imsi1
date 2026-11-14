# F50 external GLB -> OutRun native Blender overlay proof (2026-11-15)

**Status: Blender import, axis/scale/front alignment, preserved stock geometry, two actual renders, and fresh Blender re-open PASS. NOT a runnable game mod.**

This is a non-destructive, local-only prototype for replacing the OutRun 2006 Ferrari F50 model with a third-party 3D mesh. The user's verified original PMT-derived F50 Blender checkpoint is loaded from the N100 workspace. External GLB is imported as a **separate collection**; the original collection is unchanged and hidden for rendering. Two same-camera real geometry screenshots are produced.

### External source and rights
- Input: externally available `1995_ferrari_f50.glb` from `Nissmo89/Supercar-Vault-3D` (public GitHub source, GLB SHA-256 `6aa960b4d79f5e9400aaa804c2301f3c344461a88abc264d131b567575cae2dc`).
- GLB asset metadata: Ddiaz Design, source Sketchfab `9d7ec096be3546e3967ebdb5e4a87e31`, CC-BY-4.0 **claimed**.
- Source mesh names contain `CrewRecycled`, potentially indicating a ripped commercial-game asset. **Underlying rights are not confirmed. Do not copy/upload/release the third-party GLB, the derived .blend or game source assets publicly.** No external binary is committed on this GitHub branch.
- Original PC game PMT SHA-256 `10daa1312b6cff0267b38b4c440c6007c68b470a225ca15f0c324876fd80aeab`. Original PMT is not written.

### Measured result
| | OutRun PMT Blender | External GLB Blender |
|---|---:|---:|
| Mesh objects | 42 | 875 |
| Vertices | 29,049 | 195,104 |
| Triangles | 50,809 | 218,664 |
| Length after uniform fit | 4.436676 m | 4.436676 m |
| Native mesh changed | No | N/A |

- Final local Blender checkpoint: `/home/chatgpt-runner/mod_trials/f50_glb_poc_20261115/F50_EXTERNAL_OVERLAY_FINAL_TEST.blend`
- Private ZIP: `/home/chatgpt-runner/mod_trials/f50_glb_poc_20261115/F50_PRIVATE_BLENDER_POC_20261115.zip` (SHA-256 `49356fe9b750af4f3ba674e2bd542d032e69c2649231e583693921aca1eb7b8e`).
- Final independent Blender re-open: PASS. The original 42 meshes retain source fingerprint `92e400758901234d3a523b6b36b0b1cdea4d9dcae50e13ee7cdd1dfc227a1fc9`.
- Same-camera actual preview images: `F50_ORIGINAL_FULL_REAL.png`, `F50_EXTERNAL_FULL_REAL.png` (kept private on N100).

### Reproduction
On N100 in Blender 4.5.15 LTS, run `f50_glb_onepass.py` then `verify_independent.py` through Blender background Python. Paths are deliberately fixed to the user's existing private N100 layout. The input GLB is **not bundled** in this public branch.

### Before game testing
This is **not** PMT serialization, OVC/OVC3 mesh replacement or an installable OutRun mod. The mesh has ~4.3x the original triangle count and 875 separate draw objects: merge/LOD/texture-budget and wheel & animation mapping are required; next verify export format support and PC/Quest runtime rendering. No game files or existing automatic rework slot workpacks were changed.
