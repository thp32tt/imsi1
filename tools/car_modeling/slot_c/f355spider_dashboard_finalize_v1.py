#!/usr/bin/env python3
"""Publish verified native F355 Spider dashboard pass to existing slot C SSOT."""
from pathlib import Path
import json,hashlib
ROOT=Path("/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-dashboard-20261110")
Q=ROOT/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json"
W=ROOT/"docs/automation/FERRARI_COCKPIT_WORKPACK_C_F355SPIDER.json"
O=ROOT/"artifacts/slot_C/f355spider/dashboard_v1"
RC=O/"receipt.json"
MF=O/"manifest.json"
BLEND="F355Spider_OriginalPMT_Dashboard_CenterVent_Facia_v1.blend"
SOURCE=ROOT/"tools/car_modeling/slot_c/f355spider_dashboard_native_vent_v1.py"
GUARD=ROOT/"tools/car_modeling/workspace_guard.py"
IMAGES=["dashboard_detail_before.png","dashboard_detail_after.png","dashboard_detail_delta.png","dashboard_context_before.png","dashboard_context_after.png","dashboard_context_delta.png"]
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for x in iter(lambda:f.read(1048576),b""):h.update(x)
 return h.hexdigest()
def rel(p):return str(p.relative_to(ROOT))
q=json.loads(Q.read_text());w=json.loads(W.read_text());rec=json.loads(RC.read_text())
from sys import path as syspath
syspath.insert(0,str(ROOT/"tools/car_modeling"))
from workspace_guard import preflight,verify_receipt
assert q["active_by_slot"]["C"]=="f355spider" and q["active_by_slot"]["A"]=="360spider"
assert w["car_id"]=="f355spider" and w["slot"]=="C"
assert preflight(q,w,"C","dashboard")=="PASS C/f355spider target=dashboard turn=1/2"
assert rec["task_id"]=="FERRARI16-SLOTC-F355SPIDER-DASHBOARD-NATIVE-PMT019-V1-20261110"
assert rec["independent_reopen"]=="PASS_BLENDER_4_5_15_SEPARATE_PROCESS"
assert rec["input_sha256"]==w["latest_accepted_editable_blend_sha256"]
assert rec["output_sha256"]!=rec["input_sha256"]
assert rec["unchanged_other_native_meshes"]==95 and rec["changed_existing_vertices"]==8
assert rec["closest_protected_surface_after_m"]>.065
assert verify_receipt(q,w,"C",rec,O/BLEND).startswith("PASS ")
assert all((O/n).is_file() for n in IMAGES)
inputblend=ROOT/w["latest_accepted_editable_blend_file"]
assert sha(inputblend)==rec["input_sha256"]
manifest={
 "schema_version":1,"task_id":rec["task_id"],"slot":"C","car_id":"f355spider",
 "component":"dashboard","status":"COVERED_PARTIAL_QA","source_native_mesh":rec["original_mesh"],
 "original_pmt_private_path":"/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f355sp_pmt.sz",
 "original_pmt_sha256":rec["native_original_pmt_sha256"],
 "original_import_blend_sha256":rec["original_import_blend_sha256"],
 "input_blend":rel(inputblend),"input_sha256":rec["input_sha256"],
 "output_blend":rel(O/BLEND),"output_sha256":rec["output_sha256"],
 "output_size_bytes":(O/BLEND).stat().st_size,
 "modified_existing_native_vertices":rec["changed_existing_vertices"],
 "other_unchanged_native_meshes":95,"max_displacement_m":rec["max_displacement_m"],
 "closest_protected_glass_frame_surface_before_m":rec["closest_protected_surface_before_m"],
 "closest_protected_glass_frame_surface_after_m":rec["closest_protected_surface_after_m"],
 "private_photo_reference_sha256":rec["real_photo_sha256"],
 "photo_comparison":"qualitative only; not camera-registered",
 "blender_independent_reopen":rec["independent_reopen"],
 "source_script":rel(SOURCE),"source_script_sha256":sha(SOURCE),
 "workspace_guard_script_sha256":sha(GUARD),
 "receipt_sha256":sha(RC),
 "render_sha256":{n:sha(O/n) for n in IMAGES},
 "plaintext":True,"partition_required":False,"original_pmt_uploaded":False,
 "private_photos_uploaded":False,"game_exports":[],"new_textures":[],
 "whole_vehicle_qa_pass":False,"next_component":"steering_wheel"
}
MF.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
qa={
 "component":"dashboard","slot":"C","car_id":"f355spider",
 "source_modification":"True original PMT 019 twin central dashboard fascia panel; 8 existing vertices moved",
 "source_native_geometry_changed":True,"source_derived_original_meshes_changed":[rec["original_mesh"]],
 "native_original_vertices_modified":8,"max_displacement_m":rec["max_displacement_m"],
 "other_native_meshes_unchanged":95,"protected_windshield_and_frame_untouched":True,
 "windshield_protected_geometry_proximity_before_m":rec["closest_protected_surface_before_m"],
 "windshield_protected_geometry_proximity_after_m":rec["closest_protected_surface_after_m"],
 "input_blend_sha256":rec["input_sha256"],"output_blend_sha256":rec["output_sha256"],
 "independent_reopen":rec["independent_reopen"],
 "workspace_guard_verify_receipt":"PASS",
 "same_camera_before_after_png":IMAGES,
 "private_photo_reference":"REF4_interior_03_f460291745.jpg",
 "gaps":["authentic seated-driver calibrated reference is missing","whole cockpit glass-frame in-game QA not performed","full vehicle quality gate not met"],
 "full_vehicle_qa_pass":False,"part_coverage":"COVERED_PARTIAL_QA",
 "next_component":"steering_wheel"
}
(O/"QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(O/"QA.md").write_text(
 "# Ferrari F355 Spider — SLOT C dashboard source-native first pass\n\n"
 "Genuine source original PMT object: `PMT_F355SPIDER_object00_group01_material019_a0`; "
 "**8 original center dash-fascia panel vertices moved**, max 44.87 mm. "
 "This first-pass contour adjusts two existing vent panel width, height and projecting slope while preserving original faces, UVs, normals, and 95/95 other native meshes.\n\n"
 "**Windshield protection:** material004_a1 glass and material020_a0 windshield-frame candidate were observation-only; "
 "both native fingerprint SHA values remain unchanged, and minimum edited vertex-to-protected surface clearance remains >65 mm. "
 "Material017 top dash shares original source coordinates with protected windshield frame; not edited. "
 "No steering, instrument cluster, doors, seat or exterior edits.\n\n"
 "Origin SHA256: `"+rec["native_original_pmt_sha256"]+"`. "
 "Input editable Blender SHA256: `"+rec["input_sha256"]+"`. "
 "Output editable Blender SHA256: `"+rec["output_sha256"]+"`. "
 "Blender 4.5.15 independent-process reopen PASS; workspace_guard strict fresh-P0 receipt PASS.\n\n"
 "N100 authentic LHD F355 Spider interior photograph served as **qualitative** central dashboard visual reference only, "
 "not a camera-registered measurement. Original PMT package and reference photos remain private on N100; "
 "this GitHub tree contains only derived editable .blend, scripts and QA comparison renders.\n\n"
 "**Part:** COVERED_PARTIAL_QA. **Whole vehicle QA:** NOT PASS. "
 "**Next:** steering_wheel, dispatch 0/2. 24-hour car assignment unchanged. "
 "No PMT/OVC/OVC3 export, game application, exterior, new mesh, materials or textures.\n",
 encoding="utf-8")
evidence=[rel(O/BLEND),rel(RC),rel(MF),rel(O/"QA.json"),rel(O/"QA.md"),rel(SOURCE),rel(GUARD)]+[rel(O/n) for n in IMAGES]
p=w["components"]["dashboard"]
assert p["status"]=="NOT_STARTED" and p["source_edits_this_phase"]==0 and p["dispatches_consumed_this_phase"]==0
p.update({"status":"COVERED_PARTIAL_QA","source_edits_this_phase":1,"dispatches_consumed_this_phase":1,"evidence_refs":evidence,"last_saved_blend_sha256":rec["output_sha256"],"blocking_reason":None})
w["latest_accepted_editable_blend_file"]=rel(O/BLEND)
w["latest_accepted_editable_blend_sha256"]=rec["output_sha256"]
w["migration_input_blend_file"]=rel(O/BLEND)
w["migration_input_blend_sha256"]=rec["output_sha256"]
w["last_material_component"]="dashboard"
w["current_component"]="steering_wheel"
w["dispatches_on_component"]=0
w["full_vehicle_qa_pass"]=False
w["notes"]="Native F355 Spider PMT019 dashboard center 8 existing vertices shaped up to 44.87mm, 95 other original meshes unchanged; windshield safe clearance 71.76mm, Blender reopen PASS; next steering_wheel, vehicle QA NOT PASS."
car=next(c for c in q["cars"] if c["id"]=="f355spider")
assert car["slot"]=="C" and car["status"]=="ACTIVE"
assert car["strategy_v3_next_component"]=="dashboard"
assert car["source_provenance"]["original_game_resource_sha256"]==rec["native_original_pmt_sha256"]
car["output_scene_sha256"]=rec["output_sha256"]
car["strategy_v3_next_component"]="steering_wheel"
car["geometry_gate"]="PARTIAL_NEEDS_QA"
car["notes"]="Native F355 Spider PMT019 center-dashboard fascia first-pass edited 8 pre-existing vertices; 95 unrelated native meshes unchanged; Blender reopen PASS; next steering_wheel. Whole vehicle NOT PASS."
car["last_slot_c_dashboard"]={
 "component":"dashboard","status":"COVERED_PARTIAL_QA","native_mesh":rec["original_mesh"],
 "vertices_modified":8,"other_native_meshes_unchanged":95,
 "input_sha256":rec["input_sha256"],"output_sha256":rec["output_sha256"],
 "independent_reopen":"PASS","full_vehicle_qa_pass":False,
 "next_component":"steering_wheel","manifest":rel(MF)}
Q.write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
W.write_text(json.dumps(w,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"phase":"COVERED_PARTIAL_QA","original_mesh":rec["original_mesh"],"changed_vertices":8,"next":"steering_wheel","dispatch":0,"sha":rec["output_sha256"],"manifest":rel(MF)}))