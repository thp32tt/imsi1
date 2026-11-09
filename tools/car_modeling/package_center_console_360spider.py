#!/usr/bin/env python3
"""Publish the verified 360 Spider A center-console receipt into per-car GitHub workpack.
No new PMT conversion, textures, synthetic geometry or glass edits.
"""
import json,hashlib
from pathlib import Path
ROOT=Path("/home/chatgpt-runner/imsi1_slotA_360sp_console_20261110")
PART=ROOT/"artifacts/slot_A/360spider/center_console_20261110"
WORK=ROOT/"docs/automation/FERRARI_COCKPIT_WORKPACK_A_360SPIDER.json"
QUEUE=ROOT/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json"
SRC=ROOT/"artifacts/slot_A/360spider/source_bootstrap/Ferrari360Spider_OriginalPMT_EditableBaseline.blend"
OUT=PART/"Ferrari360Spider_CenterConsole_SourceEdit_R01.blend"
RECEIPT=PART/"receipt.json"
PMT=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_360sp_pmt.sz")
M={
 "task_id":"FERRARI16-SLOTA-360SPIDER-CENTER-CONSOLE-ORIGINAL-PMT-20261110-5DABFFB5",
 "slot":"A","car_id":"360spider","component":"center_console",
 "status":"COVERED_PARTIAL_QA","full_vehicle_qa_pass":False,
 "source_pmt_sha256":"a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6",
 "source_pmt_path_n100_only":str(PMT),
 "input_blend_sha256":"b4f1d071119693172bbf786809da62dce8acb0c84e52d9779a6b1a996654ce57",
 "output_blend_sha256":"5dabffb52ae4136b6b72f99c7975b629820f839afec2048e59035cb74d8ee612",
}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SRC)==M["input_blend_sha256"] and sha(OUT)==M["output_blend_sha256"] and sha(PMT)==M["source_pmt_sha256"]
q=json.loads(QUEUE.read_text())
w=json.loads(WORK.read_text())
r=json.loads(RECEIPT.read_text())
diff=json.loads((PART/"visual_diff_metrics.json").read_text())
assert q["active_by_slot"]["A"]==w["car_id"]=="360spider"
assert w["current_component"]=="center_console" and w["dispatches_on_component"]==0
assert w["components"]["center_console"]["status"]=="NOT_STARTED"
assert w["latest_accepted_editable_blend_sha256"]==M["input_blend_sha256"]
assert r["independent_reopen"].startswith("PASS") and r["changed_existing_vertices"]==16
assert r["modified_objects"]==["PMT_object00_group01_material010_a0"] and r["unchanged_other_native_meshes"]==74
assert r["windshield_and_other_regions_untouched"] is True and r["full_vehicle_qa_pass"] is False
assert diff["top"]["changed_RGB_pixels_gt3"]>1000 and diff["oblique"]["changed_RGB_pixels_gt3"]>1000
assert not (PART/"manifest.json").exists(),"already packaged"
record_files=[
 "Ferrari360Spider_CenterConsole_SourceEdit_R01.blend",
 "receipt.json","before_top.png","after_top.png","comparison_top.png",
 "before_oblique.png","after_oblique.png","comparison_oblique.png","visual_diff_metrics.json",
]
M["input"]={"path":"artifacts/slot_A/360spider/source_bootstrap/"+SRC.name,"sha256":sha(SRC),"bytes":SRC.stat().st_size}
M["output"]={"path":"artifacts/slot_A/360spider/center_console_20261110/"+OUT.name,"sha256":sha(OUT),"bytes":OUT.stat().st_size}
M["files"]={f:{"sha256":sha(PART/f),"bytes":(PART/f).stat().st_size} for f in record_files}
M["source_script"]={"path":"tools/car_modeling/source_edit_center_console_360spider.py",
 "sha256":sha(ROOT/"tools/car_modeling/source_edit_center_console_360spider.py")}
M["render_reference_only"]=["01_interior.jpg","02_interior.jpg","REF12_transmission_1_1976f73709.jpg","REF9_transmission_01_d60f697f6.jpg"]
M["private_photo_materials_exported"]=False
M["native_meshes_modified"]=1
M["existing_vertices_modified"]=16
M["other_original_meshes_unchanged"]=74
M["protected_front_glass_mesh_or_transform_changes"]=0
M["dispatches_consumed_for_result"]=1
M["next_component"]="driver_controls"
M["sha256_of_partNN_required"]=False
(PART/"manifest.json").write_text(json.dumps(M,indent=2,ensure_ascii=False)+"\n")
qa=f"""# Ferrari 360 Spider — SLOT A Center Console Original-PMT Geometry R01

- Status: **COVERED_PARTIAL_QA**; whole-car QA: **NOT PASS**
- Original source: N100 read-only `obj_plcar_360sp_pmt.sz` SHA256 `{M['source_pmt_sha256']}`
- Input native editable Blender SHA256 `{M['input_blend_sha256']}`
- Output editable Blender SHA256 `{M['output_blend_sha256']}`
- Changed exactly **16 source-native existing vertices** of `PMT_object00_group01_material010_a0`; 74 other native mesh geometry fingerprints remained identical. No added/deleted faces, no synthetic model.
- Source islands top (1412..1421), left (1384..1389), right (1350..1355): moved only 16 upper-ridge vertices; lower anchors untouched; top +2.5–6.8 cm and shoulder width +1.0–1.4 cm on each side.
- Compared with N100 locally retained Ferrari 360 Spider interior photos `01_interior.jpg`, `02_interior.jpg` and center-tunnel/gear-selector photos `REF12_transmission_1_1976f73709.jpg`, `REF9_transmission_01_d60f697f6.jpg`. The authentic photos show a comparatively higher/defined silver central tunnel/selector bridge. This is a limited geometric first-pass improvement of the *existing low-poly source tunnel*, not a reconstruction of unmodeled switchgear.
- Pixel delta across equivalent isolated original-mesh Blender cameras: top **{diff['top']['changed_RGB_pixels_gt3']:,} / 660,000** pixels; oblique **{diff['oblique']['changed_RGB_pixels_gt3']:,} / 660,000** pixels (RGB channel delta >3). These are render-change checks, not fidelity scores.
- Actual Blender 4.5.15 SAVE/INDEPENDENT REOPEN + original PMT SHA + all-native mesh IDs + normals/UV/topology + 74 other fingerprints: **PASS**.
- Windshield glass, frame, A-pillars, seals, windshield-adjacent geometry: **0 edits**; steering/dashboard **0 edits**; exterior/wheels **0 edits**.
- Original .sz and private unmodified photos: N100 only. No OVC, OVC3, PMT export, game integration, new textures, PBR, Dino, Model2.
- Remaining blockers: accurate cockpit/photo calibration, per-frame matched in-game driver eye and missing high-detail switchgear. **Full vehicle QA remains NOT PASS.**
- Source edit complete on first dispatch: next assigned region **driver_controls** (no more center-console polishing).

## Before/after native source renders

Top: ![before-after top](comparison_top.png)

Oblique: ![before-after oblique](comparison_oblique.png)
"""
(PART/"QA.md").write_text(qa)
w["components"]["center_console"].update({
 "status":"COVERED_PARTIAL_QA",
 "source_edits_this_phase":1,
 "dispatches_consumed_this_phase":1,
 "last_saved_blend_sha256":M["output_blend_sha256"],
 "evidence_refs":[
   "tools/car_modeling/source_edit_center_console_360spider.py",
   "artifacts/slot_A/360spider/center_console_20261110/receipt.json",
   "artifacts/slot_A/360spider/center_console_20261110/manifest.json",
   "artifacts/slot_A/360spider/center_console_20261110/QA.md",
   "artifacts/slot_A/360spider/center_console_20261110/Ferrari360Spider_CenterConsole_SourceEdit_R01.blend",
   "artifacts/slot_A/360spider/center_console_20261110/comparison_top.png",
   "artifacts/slot_A/360spider/center_console_20261110/comparison_oblique.png",
 ],
 "qa_gate":"SOURCE_GEOMETRY_AND_INDEPENDENT_REOPEN_PASS; MATCHED_PRIVATE_PHOTO_CALIBRATION_PENDING",
 "modified_original_mesh":"PMT_object00_group01_material010_a0",
 "native_vertices_changed":16,
 "unchanged_original_meshes":74,
})
w["latest_accepted_editable_blend_sha256"]=M["output_blend_sha256"]
w["latest_accepted_editable_blend_file"]=M["output"]["path"]
w["current_component"]="driver_controls"
w["dispatches_on_component"]=0
w["last_material_task_id"]=M["task_id"]
w["full_vehicle_qa_pass"]=False
w["notes"]="2026-11-10 SLOT A 360spider center_console: 16 original PMT-native vertices source geometry edited, 74 other original meshes unchanged, independent Blender reopen+UV/normal PASS; only COVERED_PARTIAL_QA, next driver_controls. "+w.get("notes","")
WORK.write_text(json.dumps(w,ensure_ascii=False,indent=2)+"\n")
assert json.loads(WORK.read_text())["current_component"]=="driver_controls"
print(json.dumps({"result":"PACKAGE_PASS","component_advanced_to":w["current_component"],"source_vertices_changed":16,"output_sha":sha(OUT),"manifest_sha":sha(PART/"manifest.json"),"QA_sha":sha(PART/"QA.md")}))
