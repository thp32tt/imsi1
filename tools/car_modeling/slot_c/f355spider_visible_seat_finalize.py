#!/usr/bin/env python3
"""F355 Spider SLOT C visible seat accepted original-geometry checkpoint."""
from pathlib import Path
import json,hashlib
R=Path("/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-visibleseat-20261110")
A=R/"artifacts/slot_C/f355spider/visible_seat_v1"
P=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f355sp_pmt.sz")
B0=R/"artifacts/slot_C/f355spider/source_bootstrap/F355Spider_OriginalPMT_SourceBaseline_v1.blend"
B=R/"artifacts/slot_C/f355spider/center_console_v1/F355Spider_OriginalPMT_CenterConsole_GateBezel_v1.blend"
OUT=A/"F355Spider_OriginalPMT_VisibleSeat_Bolster_v1.blend"
WP=R/"docs/automation/FERRARI_COCKPIT_WORKPACK_C_F355SPIDER.json"
QP=R/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json"
PMT="d9af341653ef44371e8df2efc4024af92d7ca03665acef04a4c3c65200bb7b11"
BASE="4fa9bdc314c5e30ab890adcff160377436540646588a36f1c4c1649c5df7186e"
OLD="0c8667304fb6c527f54dd79557604e46a02270dee5a05ce37281c181db1d66f3"
TARGET="PMT_F355SPIDER_object00_group01_material027_a0"
def sha(f):
 h=hashlib.sha256()
 with f.open("rb") as s:
  for b in iter(lambda:s.read(1<<20),b""): h.update(b)
 return h.hexdigest()
assert sha(P)==PMT and sha(B0)==BASE and sha(B)==OLD
assert OUT.exists()
rec=json.loads((A/"receipt.json").read_text())
q=json.loads(QP.read_text());w=json.loads(WP.read_text())
assert q["active_by_slot"]["C"]==w["car_id"]=="f355spider" and w["slot"]=="C"
assert w["current_component"]=="visible_seat" and w["dispatches_on_component"]==0
assert w["components"]["visible_seat"]["status"]=="NOT_STARTED"
assert w["latest_accepted_editable_blend_sha256"]==OLD
assert rec["status"]=="COVERED_PARTIAL_QA" and rec["component"]=="visible_seat"
assert rec["modified_objects"]==[TARGET] and rec["original_mesh"]==TARGET
assert rec["input_sha256"]==OLD and rec["native_original_pmt_sha256"]==PMT
assert rec["original_import_blend_sha256"]==BASE
assert rec["output_sha256"]==sha(OUT)
assert rec["independent_reopen"].startswith("PASS") and rec["blender_saved"]
assert rec["changed_existing_vertices"]==106 and rec["per_seat_existing_vertex_edits"]=={"-1":53,"1":53}
before=rec["source_mesh_fingerprints_before"];after=rec["source_mesh_fingerprints_after"]
assert len(before)==96 and before.keys()==after.keys()
assert [name for name in before if before[name]!=after[name]]==[TARGET]
assert rec["unchanged_other_native_meshes"]==95
assert rec["full_vehicle_qa_pass"]==False
car=next(c for c in q["cars"] if c["id"]=="f355spider")
assert car["status"]=="ACTIVE" and car["strategy_v3_next_component"]=="visible_seat"
assert car["output_scene_sha256"]==OLD
assert not (A/"QA.json").exists() and not (A/"manifest.json").exists()
blsha=sha(OUT)
qa={
 "task_id":rec["task_id"],"slot":"C","car_id":"f355spider","component":"visible_seat",
 "status":"COVERED_PARTIAL_QA","original_native_pmt_sha256":PMT,
 "native_import_blend_sha256":BASE,"input_blend_sha256":OLD,
 "output_blend_sha256":blsha,
 "original_native_mesh_changed":[TARGET],"new_original_native_vertex_edits":106,
 "modified_vertices_per_original_seat":rec["per_seat_existing_vertex_edits"],
 "max_displacement_m":rec["max_displacement_m"],
 "other_native_mesh_fingerprints_unchanged":95,
 "blender_4_5_15_independent_reopen":rec["independent_reopen"],
 "workspace_guard_verify_receipt":"PASS C/f355spider receipt=visible_seat changed_native_objects=1",
 "before_png_sha256":sha(A/"seat_before.png"),
 "after_png_sha256":sha(A/"seat_after.png"),
 "real_photo_reference":"N100 private REF4_interior_01_4540a6cc94.jpg",
 "real_photo_alignment":"VISUAL_PROPORTION_ONLY_UNCALIBRATED",
 "private_original_pmt_photo_not_uploaded":True,
 "no_new_vertices_faces_objects_materials_textures":True,
 "protected_glass_frame_Apillars_untouched":True,
 "dashboard_steering_center_console_unchanged":True,
 "new_PMT_OVC_OVC3_game_exports":0,
 "whole_car_qa_pass":False,"next_component":"instrument_cluster",
 "next_dispatches":0
}
(A/"QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
md=("# F355 Spider / SLOT C / visible_seat\n\n"
 "Result: COVERED_PARTIAL_QA. Vehicle QA NOT PASS.\n\n"
 "Only original OutRun 2006 native source-derived seat object was changed: "+TARGET+".\n"
 "Original PMT SHA256: "+PMT+".\n"
 "Original Blender baseline SHA256: "+BASE+".\n"
 "Accepted input Blender SHA256: "+OLD+".\n"
 "Edited output Blender SHA256: "+blsha+".\n"
 "Real geometry change: 106 pre-existing vertices (53 per original seat), maximum "
 +str(round(rec["max_displacement_m"]*1000,3))+" mm, with cushion and lower-back seat bolster contours widened/raised.\n"
 "Unchanged source-native nonseat mesh geometry fingerprints: 95 of 95. Both seat parts retain their original 94 vertices, and the target retains 300 original triangles.\n"
 "Independent Blender 4.5.15 fresh reopen: PASS. workspace_guard verify-receipt: PASS.\n"
 "N100 real F355 Spider interior photo inspected for shape, not measured or camera-registered. Original photo and PMT remain private.\n"
 "No windshield glass/frame/A-pillars/border, no steering/dashboard/center console, no exterior/tyres, no Model2/Dino, no new synthetic mesh/material/texture, no game export.\n"
 "Plain editable blend, modeling script, original native mesh receipt, matched before/after PNGs and SHA256 manifest committed; no encryption.\n"
 "Advance after this one material geometry achievement to instrument_cluster, 0/2 dispatch. 24h F355 ownership not reset.\n")
(A/"QA.md").write_text(md)
files=[
 OUT,A/"receipt.json",A/"QA.json",A/"QA.md",
 A/"seat_before.png",A/"seat_after.png",
 R/"tools/car_modeling/slot_c/f355spider_visible_seat_native_bolster_v1.py",
 R/"tools/car_modeling/slot_c/f355spider_visible_seat_inspect.py",
 R/"tools/car_modeling/slot_c/f355spider_visible_seat_finalize.py"]
manifest={
 "schema_version":1,"slot":"C","car":"f355spider","component":"visible_seat",
 "status":"COVERED_PARTIAL_QA","source_pmt_sha256":PMT,"baseline_sha256":BASE,
 "input_blend_path":str(B.relative_to(R)),"input_sha256":OLD,
 "output_blend_path":str(OUT.relative_to(R)),"output_sha256":blsha,
 "plaintext":True,"encryption":False,"split_parts_required":False,
 "files":{str(f.relative_to(R)):{"bytes":f.stat().st_size,"sha256":sha(f)} for f in files},
 "whole_vehicle_qa_pass":False}
(A/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
w["components"]["visible_seat"].update({
 "status":"COVERED_PARTIAL_QA","source_edits_this_phase":1,"dispatches_consumed_this_phase":1,
 "last_saved_blend_sha256":blsha,"blocking_reason":None,
 "evidence_refs":[str(x.relative_to(R)) for x in [OUT,A/"receipt.json",A/"QA.json",A/"QA.md",A/"manifest.json",A/"seat_before.png",A/"seat_after.png"]]})
w["latest_accepted_editable_blend_sha256"]=blsha
w["latest_accepted_editable_blend_file"]=str(OUT.relative_to(R))
w["migration_input_blend_sha256"]=blsha
w["migration_input_blend_file"]=str(OUT.relative_to(R))
w["last_material_component"]="visible_seat"
w["current_component"]="instrument_cluster"
w["dispatches_on_component"]=0
w["full_vehicle_qa_pass"]=False
w["notes"]="F355 Spider PMT027 visible_seat: 106 original native vertices changed, 95 other meshes unchanged, separate Blender reopen and receipt PASS. Next instrument_cluster, vehicle QA NOT PASS."
car["output_scene_sha256"]=blsha
car["geometry_gate"]="PARTIAL_NEEDS_QA"
car["strategy_v3_next_component"]="instrument_cluster"
car["notes"]="F355 Spider original PMT027 seat 106 original vertices altered and reopened; 95 nonseat original meshes unchanged. COVERED_PARTIAL_QA, vehicle QA NOT PASS. Next instrument_cluster."
car["last_slot_c_visible_seat"]={
 "task_id":rec["task_id"],"component":"visible_seat","status":"COVERED_PARTIAL_QA",
 "native_mesh":TARGET,"native_vertices_changed":106,"original_PMT_sha256":PMT,
 "input_blend_sha256":OLD,"output_blend_sha256":blsha,
 "other_source_meshes_unchanged":95,"blender_reopen":"PASS","receipt_guard":"PASS",
 "evidence":str((A/"QA.json").relative_to(R)),
 "next_component":"instrument_cluster","full_car_QA_PASS":False}
WP.write_text(json.dumps(w,ensure_ascii=False,indent=2)+"\n")
QP.write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":"COVERED_PARTIAL_QA","component":"visible_seat","edits":106,
"output_sha256":blsha,"next":"instrument_cluster","manifest_sha256":sha(A/"manifest.json")}))
