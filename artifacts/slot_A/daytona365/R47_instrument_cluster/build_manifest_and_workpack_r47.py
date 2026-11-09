#!/usr/bin/env python3
"""Finalize only SLOT A Daytona R47 native-PMT gauge bezel evidence and state."""
import json,hashlib
from pathlib import Path
ROOT=Path("/home/chatgpt-runner")
REPO=ROOT/"worktrees/imsi1-slotA-instrument-20261109-1303"
A=REPO/"artifacts/slot_A/daytona365/R47_instrument_cluster"
DOCS=REPO/"docs/automation"
PMT=ROOT/"rea-input/outrun/outrun2006/Cars/obj_plcar_dayts_pmt.sz"
ORIG=ROOT/"work_handoff/daytona365_rework_20261107/original_game_blender/Daytona365_ORIGINAL_GAME_COCKPIT_COMPARE.blend"
INTEGRATED=ROOT/"work_handoff/ferrari16_slotA_daytona_dashboard_steering_20261108/Daytona365_SlotA_OriginalPMT005_InnerDoor_R45.blend"
OUTPUT=A/"Daytona365_NATIVE_PMT015_InstrumentCluster_R47.blend"
SRC_SHA="f393ba5c706453a4d3f71604f25cd1631594152380856462fb0a504143ba6abe"
IMP_SHA="92c82ee5c4e0631195cb314e0d8e2f56a78a6a58da3c809c46b1da0f9d2c71a3"
ACCEPT_SHA="224131c7adc928d5d6f0377d030d5a350c59b8664c13303a2731d6dfc6e9a722"
OUT_SHA="7367034bf9900e380f0f61d8d89c19322e8d22207dcba6c5124bf8f572803c28"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n")
for p,expected in ((PMT,SRC_SHA),(ORIG,IMP_SHA),(INTEGRATED,ACCEPT_SHA),(OUTPUT,OUT_SHA)):
 if not p.is_file() or sha(p)!=expected:raise RuntimeError("BLOCKED_PROVENANCE_SHA "+str(p))
qa=read(A/"native_instrument_r47_geometry_qa.json")
rv=read(A/"native_instrument_r47_fresh_reopen_qa.json")
receipt=read(A/"native_instrument_r47_receipt.json")
render=read(A/"native_instrument_r47_render_qa.json")
if receipt["output_sha256"]!=OUT_SHA or rv["output_sha256"]!=OUT_SHA or qa["changed_original_vertices"]!=20 or render["changed_pixels_max_RGB_gt_3"]<=0:
 raise RuntimeError("BLOCKED_RECEIPT_OR_RENDER")
if not all(qa["source_mesh_fingerprints_before"][k]==qa["source_mesh_fingerprints_after"][k] for k in qa["source_mesh_fingerprints_before"] if k!="PMT_object00_group01_material015_a0"):
 raise RuntimeError("BLOCKED_OTHER_NATIVE_MESH_CHANGED")
qpath=DOCS/"FERRARI16_GEOMETRY_QUEUE.json"
wpath=DOCS/"FERRARI_COCKPIT_WORKPACK_A_DAYTONA365.json"
q=read(qpath);w=read(wpath)
if q["active_by_slot"]["A"]!="daytona365" or w["slot"]!="A" or w["car_id"]!="daytona365":
 raise RuntimeError("BLOCKED_ACTIVE_VEHICLE_CHANGE")
if w["current_component"]!="instrument_cluster" or w["dispatches_on_component"]!=0 or w["components"]["instrument_cluster"]["status"]!="NOT_STARTED":
 raise RuntimeError("BLOCKED_R47_DISPATCH_NOT_AVAILABLE")
if q["repository"]!="thp32tt/imsi1" or q["branch"]!="main":raise RuntimeError("BLOCKED_SSOT")
comp=w["components"]["instrument_cluster"]
comp.update({"status":"COVERED_PARTIAL_QA","source_edits_this_phase":1,
 "dispatches_consumed_this_phase":1,
 "evidence_refs":["docs/automation/FERRARI16_SLOTA_DAYTONA_R47_INSTRUMENT_CLUSTER_20261109.md",
 "artifacts/slot_A/daytona365/R47_instrument_cluster/manifest.json"],
 "blocking_reason":None,"last_saved_blend_sha256":OUT_SHA,
 "native_original_mesh_object":"object00_group01_material015_a0","changed_existing_vertices":20,
 "original_native_connected_component_anchors":[229,253],
 "other_native_meshes_unchanged":29,"independent_reopen":"PASS",
 "postflight_guard":"PASS","matched_camera_render_pixels_changed":render["changed_pixels_max_RGB_gt_3"],
 "separate_original_native_blend_not_integrated_into_R45":True,
 "pending_qa":["calibrated_original_game_eye","seven_authentic_photo_views",
 "R45_and_R46_native_assets_not_integrated"]})
w["current_component"]="dashboard"
w["dispatches_on_component"]=0
w["last_slot_a_r47"]={"task_id":qa["task_id"],"status":"COVERED_PARTIAL_QA",
 "component":"instrument_cluster","native_modified_object":"object00_group01_material015_a0",
 "native_vertices_modified":20,"input_original_sha256":IMP_SHA,"output_native_blend_sha256":OUT_SHA,
 "source_pmt_sha256":SRC_SHA,"reopen":"PASS","receipt_guard":"PASS",
 "accepted_integrated_R45_unchanged":True,"full_vehicle_qa_pass":False,"next":"dashboard"}
w["notes"]="R47 instrument_cluster COVERED_PARTIAL_QA, native PMT015 existing 20 gauge-bezel vertices changed, 29 native meshes unchanged, saved/reopened, receipt PASS. Standalone asset not merged into integrated R45. NEXT dashboard is P0_POLISH_HOLD; no automatic polishing without new defect ID."
c=next(x for x in q["cars"] if x["id"]=="daytona365")
if c.get("slot")!="A":raise RuntimeError("BLOCKED_QUEUE_CAR_SLOT")
c["notes"]="[2026-11-09 SLOT A R47] original PMT015 gauge bezel 20 genuine vertices geometry edited; new standalone .blend saved/reopened; 29 other original meshes unchanged; COVERED_PARTIAL_QA not car QA PASS. Integrated R45 unchanged, dashboard/wheel/glass protected in this dispatch. NEXT dashboard P0 hold."
c["strategy_v3_next_component"]="dashboard"
c["last_slot_a_r47"]={"task_id":qa["task_id"],"component":"instrument_cluster",
 "status":"COVERED_PARTIAL_QA","native_object":"object00_group01_material015_a0",
 "native_changed_vertices":20,"input_native_import_sha256":IMP_SHA,"output_native_blend_sha256":OUT_SHA,
 "accepted_R45_untouched":True,"reopen":"PASS","postflight":"PASS",
 "full_car_QA_PASS":False,"next":"dashboard"}
doc=DOCS/"FERRARI16_SLOTA_DAYTONA_R47_INSTRUMENT_CLUSTER_20261109.md"
doc.write_text("""# SLOT A — Daytona original PMT015 instrument cluster R47

- Status: **COVERED_PARTIAL_QA**, **NOT full vehicle QA PASS**. Next part: `dashboard` (P0 polish hold; do not automatically edit without explicit defect).
- Real original native PMT: `obj_plcar_dayts_pmt.sz` (N100 only), SHA256 `"""+SRC_SHA+"""`.
- Native original import .blend (N100): SHA256 `"""+IMP_SHA+"""`.
- Sole modified mesh: `object00_group01_material015_a0`, actual **20 existing native PMT vertices** in two gauge-bezel strip connected components (anchors 229/253), front lip moved toward the driver by up to **7.5 mm**. Same vertices/faces, original UVs/materials retained.
- Other **29 native original meshes unchanged**, including gauge face PMT014, windshield, A-pillars, dashboard body and steering wheel.
- Output independent editable Blender `artifacts/slot_A/daytona365/R47_instrument_cluster/Daytona365_NATIVE_PMT015_InstrumentCluster_R47.blend` SHA256 `"""+OUT_SHA+"""`. Blender 4.5.15 actual save, separate-process reopen/fingerprint audit and `workspace_guard.py verify-receipt` **PASS**.
- Local photo comparison used only authentic 365 GTS/4 gauge panel close-up `REF11_steering_instrument_closeup_5769d1ef1b.jpg` and original dash interior `REF2_dashboard_original_e91527ff82f3.jpg`; these source images remain private on N100 (not included here).
- Actual before/after same-camera Blender Workbench: `Daytona365_NATIVE_PMT015_R47_BeforeAfter.png`; pixel changes RGB>3: **"""+str(render["changed_pixels_max_RGB_gt_3"])+"""**. This is not an original-game camera or complete photo QA.
- Earlier accepted integrated R45 scene SHA256 `"""+ACCEPT_SHA+"""` **unchanged**. R46 seat and R47 gauge edits are standalone original-native proofs, **not merged** into R45 and not installable game replacements.
- No PMT/OVC/OVC3 export, external wheel/body, new materials, PBR, textures, game integration or Dino/Model2 changes. No AES, Secrets or encrypted assets.
- Outstanding vehicle gate: calibrated actual driver-eye viewpoint, seven authenticated photo views, source mesh connectivity QA and standalone native-to-integrated scene QA.
""")
write(wpath,w)
write(qpath,q)
paths=sorted(p for p in A.iterdir() if p.is_file() and p.name not in ("manifest.json",))
files=[{"path":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in paths]
manifest={"schema_version":1,"task_id":qa["task_id"],"slot":"A","car_id":"daytona365",
 "component":"instrument_cluster","status":"COVERED_PARTIAL_QA","full_vehicle_qa_pass":False,
 "source_original_game_pmt_sha256":SRC_SHA,"original_import_input_blend_sha256":IMP_SHA,
 "accepted_integrated_r45_sha256_unchanged":ACCEPT_SHA,"output_blend_sha256":OUT_SHA,
 "original_pmt_and_photos_are_not_published":True,"source_blend_is_editable":True,
 "single_binary_limit_bytes":1400000,"output_blend_bytes":OUTPUT.stat().st_size,
 "plaintext_binary_split_required":OUTPUT.stat().st_size>1400000,
 "encrypted":False,"secrets_required":False,
 "modified_original_native_meshes":["object00_group01_material015_a0"],
 "native_vertices_changed":20,"native_other_meshes_unchanged":29,"blender_independent_reopen":"PASS",
 "postflight_guard":"PASS","render_comparison_pixels_changed":render["changed_pixels_max_RGB_gt_3"],
 "integrated_into_R45":False,"next":"dashboard","files":files}
if manifest["plaintext_binary_split_required"]:raise RuntimeError("BLOCKED_REQUIRES_PLAINTEXT_PARTS")
write(A/"manifest.json",manifest)
print("MANIFEST_PASS",len(files),OUTPUT.stat().st_size,"bytes","NEXT",w["current_component"])