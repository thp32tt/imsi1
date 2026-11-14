# Assetto Corsa complete-car -> OutRun 2006 manual pilot

Date: 2026-11-15 KST.
STATUS: Source inventory and Blender scene inspection tools only.
No real KN5 supplied, no KN5 geometry import performed, no PMT writer, no tested game replacement.

This feature branch is separate from Ferrari A/C modeling dispatches. Do not resume disabled automations, change active workpacks, overwrite original OutRun PMT assets, or modify production VR branches.

## Target

Replace a complete vehicle visually: exterior body, detailed cockpit, four wheels, discs, glass, lights, textures, UVs, steering animation, LODs, materials, pivot objects. Preserve existing OutRun 2006 vehicle physics, AI, gameplay, car slot, collision, MOZA force feedback and camera system.

## Step 1. Local owned source inventory (read-only)

Supply a complete legally usable Assetto Corsa car folder, for example content/cars/car_id, including the primary high-LOD KN5, other LODs, skins and preferably extracted data/lods.ini. Do not select collider.kn5 as the visible car.

    python tools/car_import/assetto_full_car_preflight.py --car-dir /private/content/cars/car_id --output /private/ac_source.json

The code records filenames, SHA-256, lengths, LOD selection and skin folder names. It does not parse geometry or convert source. A successful inventory does not imply game compatibility.

## Step 2. Independent Blender scene audit (read-only)

Import a whole car folder using a known KN5 importer, preserving native mesh hierarchy, normals, UVs, texture images and wheel / steering / cockpit pivots. Save a separate independent .blend.

KN5 Tools 2.0.3 specifies Blender 5.x; the previously recorded N100 4.5.15 should not be assumed compatible. Use a separate Blender 5.x installation for this stage, or validate an alternate importer.

    blender --background imported-car.blend --python tools/car_import/inspect_imported_car_blender.py -- --output /private/ac_scene.json

Scene inspection checks WHEEL_LF/RF/LR/RR, COCKPIT_HR/LR, STEER_HR/LR, mesh triangle count, missing UVs, object transforms, materials, textures and role coverage. It does not modify the scene, export PMT or test the game.

## Step 3. Game integration (NOT IMPLEMENTED)

1. Implement and test an Assetto Blender mesh -> OutRun compatible PMT writer, or a safe separate renderer-backed mesh replacement. Verify PMT tables, object/group/vertex identities, 16-bit indices, primitives, culling, material/texture tables, DDS alpha, LODs and format constraints. Existing source scripts are readers, not writers.
2. Map source coordinates to actual OutRun body size, seated camera, four wheel steering/spin pivots, cockpit steering wheel, doors and convertible parts where supported. Preserve unrelated resources.
3. Mount replacements from an optional external folder, with disable-and-revert behavior; do not edit original PMTs or OVC archives in place.
4. Test original car selection, third-person view, cockpit view, mirrors/glass, headlights, textures, physics continuity, both Quest 3 OpenXR eyes and frame timings for 120 Hz. Never claim an in-game QA pass from Blender-only images.

## Verified source evidence

- thp32tt/imsi1 main: tools/car_modeling/import_360spider_native_pmt.py is a source-only OutRun PMT -> Blender importer.
- thp32tt/OutRun2006Tweaks vr-dx11-native-r71: docs/file_formats/pmt_c2c.bt describes PMT layouts; it is not a converter.
- r4dius/outrun2-decomp main: src/platform/vehicle_model_draw.cpp emits multiple component draws and per-wheel transforms; src/platform/pc_pmt_loader.cpp loads PC D3D9 buffers.
- N100 rea-input scan for KN5 files: zero found on 2026-11-15. Actual imported car and game replacement remain BLOCKED_INPUT.

## Validation gates

SOURCE_VERIFIED -> SCENE_VERIFIED -> OUTRUN_FORMAT_BUILT -> IN_GAME_DRAW_PASS -> VR_STEREO_PERF_PASS.

Do not award score for status checks, dummy KN5 test bytes or documentation-only milestones. Do not publish the user-owned KN5, game models, photos or license-restricted textures.

References:
https://extensions.blender.org/add-ons/kn5-blender-tools/
https://github.com/r4dius/outrun2-decomp
https://semiloker.github.io/assetto-corsa-gltf/docs/cars/
