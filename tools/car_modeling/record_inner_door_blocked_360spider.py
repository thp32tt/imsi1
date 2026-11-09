#!/usr/bin/env python3
"""Record a verified fail-closed native inner-door inspection without using a dispatch."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2]
D=R/"artifacts/slot_A/360spider/inner_door_20261110"
Q=R/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json"
W=R/"docs/automation/FERRARI_COCKPIT_WORKPACK_A_360SPIDER.json"
ORIGINAL=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_360sp_pmt.sz")
INPUT=R/"artifacts/slot_A/360spider/center_console_20261110/Ferrari360Spider_CenterConsole_SourceEdit_R01.blend"
B_SHA="5dabffb52ae4136b6b72f99c7975b629820f839afec2048e59035cb74d8ee612"
P_SHA="a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6"
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
assert sha(INPUT)==B_SHA, "accepted input blend hash changed"
assert sha(ORIGINAL)==P_SHA, "native original source hash changed"
q=json.loads(Q.read_text());w=json.loads(W.read_text())
assert q["active_by_slot"]["A"]==w["car_id"]=="360spider"
assert w["current_component"]=="inner_door" and w["dispatches_on_component"]==0
assert w["components"]["inner_door"]["status"]=="NOT_STARTED"
assert w["latest_accepted_editable_blend_sha256"]==B_SHA
assert w["latest_accepted_editable_blend_file"]=="artifacts/slot_A/360spider/center_console_20261110/Ferrari360Spider_CenterConsole_SourceEdit_R01.blend"
assert not (D/"QA.json").exists(), "already recorded"
inventory=json.loads((D/"native_door_roi_inventory.json").read_text())["components"]
m006=[x for x in inventory if x["mesh"]=="PMT_object00_group01_material006_a0"]
m010=[x for x in inventory if x["mesh"]=="PMT_object00_group01_material010_a0"]
assert any(r["root"]==2917 and r["n"]==18 for r in m006)
assert any(r["root"]==2832 and r["n"]==39 for r in m006)
assert any(r["root"]==1492 and r["n"]==4 for r in m010)
images=["door_from_interior.png","door_from_exterior.png","mat010_interior.png"]
assert all((D/f).is_file() for f in images)
rel="artifacts/slot_A/360spider/inner_door_20261110/"
reason=("No independently attributable native original interior-door trim/armrest/handle/speaker mesh. "
 "Candidate PMT_object00_group01_material006_a0 islands 2917-2934 and 2832-2870 render as exterior body-side surfaces, "
 "while material010 includes seat/floor/cockpit surfaces without a safely isolated inner-door part. "
 "Editing either would risk exterior or adjacent protected glass-fitting geometry; source-only target was rejected. "
 "No synthetic new door mesh allowed.")
task="FERRARI16-SLOTA-360SPIDER-INNER-DOOR-NATIVE-SCOPE-BLOCKED-20261110-598DFE64"
qa={"task_id":task,"slot":"A","vehicle":"360spider","target":"inner_door","status":"BLOCKED",
    "source_mesh_changed":False,"changed_vertices":0,"changed_objects":[],"new_objects":0,"new_faces":0,
    "native_pmt_sha256":P_SHA,"original_import_blend_sha256":w["original_import_blend_sha256"],
    "input_accepted_blend_sha256":B_SHA,"output_accepted_blend_sha256":B_SHA,
    "fresh_blend_saved":False,"independent_blender_reopen":"NOT_APPLICABLE_NO_NEW_BLEND",
    "actual_geometry_change":False,"full_vehicle_qa_pass":False,"covered_partial_qa":False,
    "protected_front_glass_meshes_modified":False,"non_target_meshes_modified":False,
    "allowed_followup_component":"visible_seat","dispatch_consumed_for_check":False,
    "native_mesh_candidate_rois":[
     {"mesh":"PMT_object00_group01_material006_a0","roots":[2917,2832],"classification":"exterior side surfaces, not safely targetable inner door"},
     {"mesh":"PMT_object00_group01_material010_a0","root":1492,"classification":"mixed seat/floor/tunnel support, not isolated door trim"}
    ],
    "private_real_photo_reference":"N100/outrun2_vr_refs/20261104_16car_cockpit/04_360_Spider/REF4_interior_03_cbe6a4e606.jpg (not published)",
    "real_photo_observation":"black leather upper insert; sculpted armrest/handle; contrasting lower speaker insert",
    "blocker":reason,"render_evidence":[rel+x for x in images]}
(D/"QA.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n")
(D/"QA.md").write_text("# 360 Spider / SLOT A / inner_door – BLOCKED\n\n"
+"**Native PMT inspection only; no geometry edit, no checkpoint promotion, no dispatch consumed.**\n\n"
+"- Original OutRun PMT SHA256: `"+P_SHA+"`\n"
+"- Input/output accepted editable Blender SHA256 (unchanged): `"+B_SHA+"`\n"
+"- Inspected existing original-native PMT geometry: `PMT_object00_group01_material006_a0` and `PMT_object00_group01_material010_a0`. "
+"The first contains disjoint outer side surfaces; the second contains mixed cabin-floor/seat supports. "
+"No separately attributable, safely editable interior door card/armrest/handle/speaker group was proven.\n"
+"- Compared with private N100 Ferrari 360 Spider inner-door real photo showing black upper padded insert, armrest, silver lower speaker section. Original photo stays on N100.\n"
+"- Protected front glass/frame/A-pillars/door-body and all 75 PMT-native source object geometry remains untouched. No new mesh, no exports, no textures.\n"
+"- **BLOCKED**: "+reason+"\n"
+"- Next target: `visible_seat` (same 360spider, SLOT=A). Not a whole-car QA PASS.\n\n"
+"## Unmodified-source visual evidence\n\n"
+"- [Original PMT body-side candidates – cabin view](door_from_interior.png)\n"
+"- [Original PMT body-side candidates – exterior view](door_from_exterior.png)\n"
+"- [Original PMT mixed material010 – cabin view](mat010_interior.png)\n")
manifest={"task_id":task,"status":"BLOCKED_NO_MESH_EDIT","native_pmt_input_sha256":P_SHA,
 "original_import_blend_sha256":w["original_import_blend_sha256"],
 "input_blend_sha256":B_SHA,"output_blend_sha256":B_SHA,"new_blend_produced":False,
 "source_mesh_changed":False,"part_covered":False,"vehicle_qa_pass":False,
 "next_component":"visible_seat","files_sha256":{}}
for f in images+["QA.json","QA.md","native_door_roi_inventory.json"]:
 manifest["files_sha256"][rel+f]=sha(D/f)
(D/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
c=w["components"]["inner_door"]
c.update({"status":"BLOCKED","source_edits_this_phase":0,"dispatches_consumed_this_phase":0,
 "evidence_refs":[rel+x for x in ("QA.json","QA.md","manifest.json","native_door_roi_inventory.json",*images)],
 "last_saved_blend_sha256":None,"blocking_reason":reason,
 "geometry_edit_proved":False,"protected_regions_untouched":True})
w["current_component"]="visible_seat"
w["dispatches_on_component"]=0
w["notes"]=("2026-11-10 SLOT A 360spider inner_door BLOCKED after original PMT island/isolated render+private photo comparison: "
 "only exterior/mixed support surfaces; no safe native interior trim, no geometry edit or dispatch consumption; next visible_seat. "+w.get("notes",""))
W.write_text(json.dumps(w,indent=2,ensure_ascii=False)+"\n")
print("BLOCKED_SAFELY next",w["current_component"],"geom_changed",qa["source_mesh_changed"],
      "pmt",P_SHA,"blend",B_SHA,flush=True)