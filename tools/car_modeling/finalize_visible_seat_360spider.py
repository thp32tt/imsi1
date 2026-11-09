#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2]
D=R/"artifacts/slot_A/360spider/visible_seat_20261110"
W=R/"docs/automation/FERRARI_COCKPIT_WORKPACK_A_360SPIDER.json"
Q=R/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json"
P=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_360sp_pmt.sz")
B=R/"artifacts/slot_A/360spider/source_bootstrap/Ferrari360Spider_OriginalPMT_EditableBaseline.blend"
IN=R/"artifacts/slot_A/360spider/center_console_20261110/Ferrari360Spider_CenterConsole_SourceEdit_R01.blend"
OUT=D/"Ferrari360Spider_VisibleSeat_OriginalPMT_R02.blend"
RECEIPT=D/"receipt.json"
P_SHA="a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6"
B_SHA="b4f1d071119693172bbf786809da62dce8acb0c84e52d9779a6b1a996654ce57"
I_SHA="5dabffb52ae4136b6b72f99c7975b629820f839afec2048e59035cb74d8ee612"
O_SHA="af5a9a9d9650d261b1b24f56e5ff8b5291773e033c43087e000276940fbc87a2"
task="FERRARI16-SLOTA-360SPIDER-NATIVE-VISIBLE-SEAT-R02-20261110-AF5A9A9D"
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for part in iter(lambda:f.read(1024*1024),b""):h.update(part)
 return h.hexdigest()
assert sha(P)==P_SHA and sha(B)==B_SHA and sha(IN)==I_SHA and sha(OUT)==O_SHA
w=json.loads(W.read_text());q=json.loads(Q.read_text());rec=json.loads(RECEIPT.read_text())
assert q["active_by_slot"]["A"]==w["car_id"]=="360spider"
assert w["current_component"]=="visible_seat" and w["dispatches_on_component"]==0
assert w["components"]["visible_seat"]["status"]=="NOT_STARTED"
assert w["latest_accepted_editable_blend_sha256"]==I_SHA
assert rec["independent_reopen"].startswith("PASS_BLENDER_4_5_15")
assert rec["changed_existing_vertices"]==20 and rec["modified_objects"]==["PMT_object00_group01_material010_a0"]
assert rec["unchanged_other_native_meshes"]==74 and rec["nonseat_components_within_target_unchanged"]
assert rec["original_import_blend_sha256"]==B_SHA and rec["native_original_pmt_sha256"]==P_SHA
assert rec["input_sha256"]==I_SHA and rec["output_sha256"]==O_SHA
assert not w["full_vehicle_qa_pass"] and not rec["full_vehicle_qa_pass"]
assert w["components"]["instrument_cluster"]["status"]=="NOT_STARTED"
images=["before_seat_driver_top.png","after_seat_driver_top.png",
        "before_seat_driver_oblique.png","after_seat_driver_oblique.png",
        "comparison_seat_before_after.jpg"]
assert all((D/i).is_file() for i in images)
qa={
 "task_id":task,"slot":"A","car_id":"360spider","component":"visible_seat",
 "status":"COVERED_PARTIAL_QA","vehicle_complete":False,"whole_car_qa_pass":False,
 "original_native_pmt_sha256":P_SHA,"original_import_blend_sha256":B_SHA,
 "input_blend_sha256":I_SHA,"output_blend_sha256":O_SHA,
 "original_mesh_changed":"PMT_object00_group01_material010_a0",
 "original_native_vertices_changed":20,"original_meshes_unchanged":74,
 "previous_accepted_console_vertices_unchanged":True,
 "front_windshield_frame_A_pillar_glass_fit_unchanged":True,
 "new_meshes":0,"new_textures":0,"exported_pmt_ovc_ovc3":False,
 "fresh_blender_reopen":"PASS","workspace_guard_receipt":"PASS",
 "target_subregions":["driver and passenger lumbar backrest", "side bolsters", "front seat-cushion support"],
 "photo_reference_N100_only":"outrun2_vr_refs/20261104_16car_cockpit/04_360_Spider/01_interior.jpg",
 "real_world_photo_assessment":"Original black leather sport seats show padded lumbar and profiled side bolsters. First-pass local native geometry refinement only; original upholstery ribbing, leather finish and true camera calibration unverified.",
 "visual_evidence":images,
 "remaining_qa_blockers":["exact original-game seated driver-eye view not calibrated","matched genuine photos only qualitative","full car QA has not passed"],
 "next":"instrument_cluster","outstanding_vehicle_qa":"NOT_PASS"}
(D/"QA.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n")
(D/"QA.md").write_text(f"""# Ferrari 360 Spider / SLOT A / native visible-seat first-pass geometry

Status: COVERED_PARTIAL_QA. Whole-car QA NOT PASS. One actual native geometry edit.

- Native original PMT SHA256: {P_SHA}. Kept on N100 only.
- Original imported editable Blender SHA256: {B_SHA}.
- Accepted input center console Blender SHA256: {I_SHA}.
- Editable output seat Blender SHA256: {O_SHA}.
- Original mesh PMT_object00_group01_material010_a0: 20 existing native seat vertices changed. Local seat backrest toward occupants up to 38 mm, seat bolsters up to 18 mm, front seat-cushion lift up to 30 mm, both left and right seat sides. No added objects or faces. Original UV/normals/topology preserved.
- Previous accepted center-console vertices unchanged. Other 74 native meshes unchanged, windshield/front-glass/frame/A-pillars and adjoining seals unchanged.
- Authentic photo reference: private N100 360 Spider interior 01_interior.jpg; broad seat/bolster profile only. No exact photo registration or game-driver-eye equivalence claimed.
- Blender 4.5.15 independent clean reopen native geometry/UV/normal/75-mesh fingerprint PASS. workspace_guard.py verify-receipt PASS.
- No synthetic mesh, textures, exterior/wheel edits, OVC/OVC3/PMT export, game integration, Model2 or Dino.
- Matched BEFORE/AFTER camera comparison: comparison_seat_before_after.jpg; before/after oblique and top PNG evidence.
- Next target instrument_cluster (0/2). 24h vehicle assignment stays. Full vehicle photo/camera quality gate pending.
""")
base="artifacts/slot_A/360spider/visible_seat_20261110/"
included=["Ferrari360Spider_VisibleSeat_OriginalPMT_R02.blend","receipt.json","QA.json","QA.md",
 *images,"material010_connected_islands.json"]
scripts=["tools/car_modeling/source_edit_visible_seat_360spider.py",
         "tools/car_modeling/seat_islands_360spider.py"]
man={"schema":1,"task_id":task,"slot":"A","car":"360spider","component":"visible_seat",
 "input_blend_sha256":I_SHA,"output_blend_sha256":O_SHA,
 "original_native_PMT_sha256":P_SHA,"original_import_blend_sha256":B_SHA,
 "input_blend_path":str(IN.relative_to(R)),"output_blend_path":str(OUT.relative_to(R)),
 "source_mesh_changed":True,"native_vertices_changed":20,"native_meshes_changed":1,
 "other_original_native_meshes_unchanged":74,"whole_vehicle_QA_pass":False,
 "plain_unencrypted":True,"multipart_binary_required":False,
 "original_PMT_and_full_photo_remain_N100":True,"file_sha256":{}}
for name in included:man["file_sha256"][base+name]=sha(D/name)
for path in scripts:man["file_sha256"][path]=sha(R/path)
(D/"manifest.json").write_text(json.dumps(man,indent=2)+"\n")
c=w["components"]["visible_seat"]
c.update({"status":"COVERED_PARTIAL_QA","source_edits_this_phase":1,"dispatches_consumed_this_phase":1,
  "evidence_refs":[base+f for f in ["receipt.json","QA.json","QA.md","manifest.json",
     "Ferrari360Spider_VisibleSeat_OriginalPMT_R02.blend","comparison_seat_before_after.jpg",
     "before_seat_driver_oblique.png","after_seat_driver_oblique.png"]]+scripts,
  "last_saved_blend_sha256":O_SHA,"qa_gate":"NATIVE_SOURCE_GEOMETRY_AND_FRESH_REOPEN_PASS; GENUINE_PHOTO_CALIBRATION_PENDING",
  "modified_original_mesh":"PMT_object00_group01_material010_a0",
  "native_vertices_changed":20,"unchanged_original_meshes":74,
  "nonseat_components_within_target_unchanged":True,"protected_regions_untouched":True})
w["current_component"]="instrument_cluster";w["dispatches_on_component"]=0
w["latest_accepted_editable_blend_sha256"]=O_SHA
w["latest_accepted_editable_blend_file"]=str(OUT.relative_to(R))
w["last_material_task_id"]=task
w["notes"]=("2026-11-10 360spider visible_seat: 20 original PMT native vertices changed, previous console and 74 other meshes preserved, independent reopen & workspace guard PASS, COVERED_PARTIAL_QA only. Next instrument_cluster. "+w.get("notes",""))
W.write_text(json.dumps(w,indent=2,ensure_ascii=False)+"\n")
print("READY_FOR_GITHUB",task,"input",I_SHA,"output",O_SHA,"next",w["current_component"],"files",len(man["file_sha256"]))