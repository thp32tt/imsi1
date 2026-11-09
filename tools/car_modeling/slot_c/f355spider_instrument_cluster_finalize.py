#!/usr/bin/env python3
"""Integrate one verified F355 Spider SLOT=C native instrument-cluster checkpoint into imsi1 SSOT."""
from pathlib import Path
import json,hashlib,sys,datetime
ROOT=Path("/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-instrument-20261110")
QP=ROOT/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json"
WP=ROOT/"docs/automation/FERRARI_COCKPIT_WORKPACK_C_F355SPIDER.json"
DIR=ROOT/"artifacts/slot_C/f355spider/instrument_cluster_v1"
SCRIPT=ROOT/"tools/car_modeling/slot_c/f355spider_instrument_cluster_native_v1.py"
RC=DIR/"receipt.json";MF=DIR/"manifest.json"
RENDER_NAMES=["cluster_before.png","cluster_after.png","cluster_delta.png","driver_context_before.png","driver_context_after.png","driver_context_delta.png"]
BLEND="F355Spider_OriginalPMT_InstrumentCluster_Visor_v1.blend"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def main():
 sys.path.insert(0,str(ROOT/"tools/car_modeling"))
 from workspace_guard import preflight,verify_receipt
 queue=json.loads(QP.read_text(encoding="utf-8"))
 w=json.loads(WP.read_text(encoding="utf-8"))
 rec=json.loads(RC.read_text(encoding="utf-8"))
 assert queue["active_by_slot"]["C"]=="f355spider"
 assert w["slot"]=="C" and w["car_id"]=="f355spider"
 assert preflight(queue,w,"C","instrument_cluster")=="PASS C/f355spider target=instrument_cluster turn=1/2"
 assert rec["task_id"]=="FERRARI16-SLOTC-F355SPIDER-INSTRUMENT-CLUSTER-NATIVE-PMT016-V1-20261110"
 assert rec["input_sha256"]==w["latest_accepted_editable_blend_sha256"]
 assert rec["input_sha256"]=="6b179f9d275226ade32960ac49f52cec8149247dc43726f311cb79beeeb06802"
 assert rec["output_sha256"]=="ec320da62a7ac21bf88cef5ed205558f3542e03f6f35d6f76de5d4e3d7643e23"
 assert rec["changed_existing_vertices"]==40
 assert rec["source_mesh_fingerprints_before"]["PMT_F355SPIDER_object00_group01_material011_a0"]==rec["source_mesh_fingerprints_after"]["PMT_F355SPIDER_object00_group01_material011_a0"]
 assert verify_receipt(queue,w,"C",rec,DIR/BLEND).startswith("PASS C/f355spider")
 assert all((DIR/n).is_file() for n in RENDER_NAMES)
 input_file=ROOT/"artifacts/slot_C/f355spider/visible_seat_v1/F355Spider_OriginalPMT_VisibleSeat_Bolster_v1.blend"
 assert sha(input_file)==rec["input_sha256"]
 manifest={
  "schema_version":1,"task_id":rec["task_id"],"slot":"C","vehicle":"f355spider",
  "component":"instrument_cluster","status":"COVERED_PARTIAL_QA",
  "input_blend_relative_path":str(input_file.relative_to(ROOT)),
  "input_blend_sha256":rec["input_sha256"],"output_blend_relative_path":str((DIR/BLEND).relative_to(ROOT)),
  "output_blend_sha256":rec["output_sha256"],"output_blend_size_bytes":(DIR/BLEND).stat().st_size,
  "original_pmt_private_source_path":"/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f355sp_pmt.sz",
  "original_pmt_sha256":rec["native_original_pmt_sha256"],
  "original_import_blend_sha256":rec["original_import_blend_sha256"],
  "reference_private_photo_sha256":rec["photo_reference_sha256"],
  "source_native_object":rec["original_mesh"],"changed_native_vertices":rec["changed_existing_vertices"],
  "untouched_other_native_meshes":rec["unchanged_other_native_meshes"],
  "independent_blender_reopen":rec["independent_reopen"],
  "script_relative_path":str(SCRIPT.relative_to(ROOT)),"script_sha256":sha(SCRIPT),
  "receipt_sha256":sha(RC),
  "renders_sha256":{n:sha(DIR/n) for n in RENDER_NAMES},
  "plaintext":True,"partitions_required":False,"game_exports":False,
  "full_vehicle_qa_pass":False,
  "private_reference_photos_committed":False,"original_pmt_committed":False,
  "next_component":"dashboard"
 }
 MF.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 qa={
  "task_id":rec["task_id"],"component":"instrument_cluster","slot":"C","car":"f355spider",
  "native_original_mesh_modified":rec["modified_objects"],"source_existing_vertices_moved":rec["changed_existing_vertices"],
  "max_movement_m":rec["max_displacement_m"],"other_original_meshes_unchanged":95,
  "instrument_gauge_face_untouched":True,"protected_windshield_glass_frame_apillars_untouched":True,
  "blender_separate_process_reopen":rec["independent_reopen"],"guard_verify_receipt":"PASS",
  "comparison_render":"cluster_before.png vs cluster_after.png; driver_context_before.png vs driver_context_after.png",
  "private_photo_used":"REF4_interior_01_4540a6cc94.jpg","photo_comparison":"F355 LHD black hood around triple circular gauges; qualitative shape only; registered driver eye not available",
  "qa_limitations":["game camera not calibrated to photograph","gauge artwork/textures unchanged","Blender visual QA cannot prove original-game visibility","whole cockpit seam review outstanding"],
  "status":"COVERED_PARTIAL_QA","whole_car_qa_pass":False,"next":"dashboard"
 }
 (DIR/"QA.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 (DIR/"QA.md").write_text(
  "# F355 Spider / SLOT C / native instrument_cluster pass\n\n"
  "- **Geometry:** only existing PMT `object00_group01_material016_a0` upper gauge-binnacle visor vertices, **40 moved**; max **34.12 mm**. No topology, object transform, material or texture change.\n"
  "- **Unchanged:** 95 other PMT-derived native Blender meshes, the separate instrument gauge face PMT011, previous center console/seat, steering wheel, dashboard outside the target, windshield/glass/frame/A-pillar/borders and all exterior parts.\n"
  "- **Source:** native N100 original PMT SHA256 `"+rec["native_original_pmt_sha256"]+"`, source baseline SHA256 `"+rec["original_import_blend_sha256"]+"`. No original PMT or private photograph uploaded.\n"
  "- **Input .blend:** `"+rec["input_sha256"]+"`. **Output .blend:** `"+rec["output_sha256"]+"`. Original 96 mesh identities retained.\n"
  "- **Validation:** Blender 4.5.15 separate process save/reopen PASS, `workspace_guard verify-receipt` PASS, same-camera before/after and delta PNGs in this directory; source-native fingerprint receipt attached.\n"
  "- **Reference:** N100 private LHD F355 Spider interior photo; gauge-cluster hood silhouette visually consulted, **not camera registered or dimensionally measured**. Gaming test, calibrated driver-eye and comprehensive cabin seam QA remain outstanding.\n"
  "- **Gate:** `COVERED_PARTIAL_QA` for this part; full vehicle QA **NOT PASS**. Next part `dashboard` (fresh initial pass, no historical steering/dashboard micro-polish loops).\n",
  encoding="utf-8")
 refs=[
  str((DIR/BLEND).relative_to(ROOT)),str(RC.relative_to(ROOT)),str(MF.relative_to(ROOT)),
  str((DIR/"QA.json").relative_to(ROOT)),str((DIR/"QA.md").relative_to(ROOT)),
 ]+[str((DIR/n).relative_to(ROOT)) for n in RENDER_NAMES]+[str(SCRIPT.relative_to(ROOT))]
 item=w["components"]["instrument_cluster"]
 assert item["status"]=="NOT_STARTED" and item["source_edits_this_phase"]==0 and item["dispatches_consumed_this_phase"]==0
 item.update({"status":"COVERED_PARTIAL_QA","source_edits_this_phase":1,"dispatches_consumed_this_phase":1,"evidence_refs":refs,"last_saved_blend_sha256":rec["output_sha256"],"blocking_reason":None})
 w["latest_accepted_editable_blend_sha256"]=rec["output_sha256"]
 w["latest_accepted_editable_blend_file"]=str((DIR/BLEND).relative_to(ROOT))
 w["migration_input_blend_sha256"]=rec["output_sha256"]
 w["migration_input_blend_file"]=str((DIR/BLEND).relative_to(ROOT))
 w["last_material_component"]="instrument_cluster"
 w["current_component"]="dashboard"
 w["dispatches_on_component"]=0
 w["full_vehicle_qa_pass"]=False
 w["notes"]="F355 Spider native PMT016 instrument visor 40 original verts moved (max 34.12mm), 95 other native meshes unchanged, source Blender separate reopen PASS; dashboard next, vehicle QA NOT PASS."
 car=next(c for c in queue["cars"] if c["id"]=="f355spider")
 assert car["slot"]=="C" and car["status"]=="ACTIVE"
 assert car["source_provenance"]["original_game_resource_sha256"]==rec["native_original_pmt_sha256"]
 assert car["strategy_v3_next_component"]=="instrument_cluster"
 car["output_scene_sha256"]=rec["output_sha256"]
 car["geometry_gate"]="PARTIAL_NEEDS_QA"
 car["strategy_v3_next_component"]="dashboard"
 car["notes"]="Original PMT016 instrument-cluster visor edited 40 vertices; independent Blender reopen and source proof PASS. Scope COVERED_PARTIAL_QA only; next dashboard; whole-car QA NOT PASS."
 car["last_slot_c_instrument_cluster"]={"component":"instrument_cluster","status":"COVERED_PARTIAL_QA","native_mesh":rec["original_mesh"],"changed_existing_vertices":40,"other_native_meshes_unchanged":95,"input_sha256":rec["input_sha256"],"output_sha256":rec["output_sha256"],"reopen":"PASS","full_vehicle_qa_pass":False,"next":"dashboard","manifest":str(MF.relative_to(ROOT))}
 QP.write_text(json.dumps(queue,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 WP.write_text(json.dumps(w,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps({"slot":"C","car":"f355spider","completed":"instrument_cluster","next":w["current_component"],"out_sha":rec["output_sha256"],"qa":"COVERED_PARTIAL_QA","dispatch_next":w["dispatches_on_component"],"manifest":str(MF.relative_to(ROOT))}))
if __name__=="__main__":main()