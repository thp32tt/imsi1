#!/usr/bin/env python3
"""Fail-closed V4 Daytona R45+R46/R47 original-object integration audit.
Writes only slot A QA evidence and its workpack; never edits native game assets,
windshield/steering/dashboard, raw PMT, private photos, or other slots.
"""
from pathlib import Path
import hashlib, json, re
BASE=Path("/home/chatgpt-runner")
REPO=BASE/"imsi1_slotA_crossqa_20261109"
DEST=REPO/"artifacts/slot_A/daytona365/cross_cockpit_qa_v4_integration_20261109"
QUEUE=REPO/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json"
WORK=REPO/"docs/automation/FERRARI_COCKPIT_WORKPACK_A_DAYTONA365.json"
NATIVE=BASE/"rea-input/outrun/outrun2006/Cars/obj_plcar_dayts_pmt.sz"
ORIGINAL=BASE/"work_handoff/daytona365_rework_20261107/original_game_blender/Daytona365_ORIGINAL_GAME_COCKPIT_COMPARE.blend"
R45=BASE/"work_handoff/ferrari16_slotA_daytona_dashboard_steering_20261108/Daytona365_SlotA_OriginalPMT005_InnerDoor_R45.blend"
R46=REPO/"artifacts/slot_A/daytona365/R46_visible_seat/Daytona365_NATIVE_PMT017_VisibleSeat_R46.blend"
R47=REPO/"artifacts/slot_A/daytona365/R47_instrument_cluster/Daytona365_NATIVE_PMT015_InstrumentCluster_R47.blend"
SOURCES={"original_game_pmt":NATIVE,"original_import_blend":ORIGINAL,"accepted_R45_blend":R45,"standalone_R46_seat_blend":R46,"standalone_R47_gauge_blend":R47}
EXPECTED={"original_game_pmt":"f393ba5c706453a4d3f71604f25cd1631594152380856462fb0a504143ba6abe","original_import_blend":"92c82ee5c4e0631195cb314e0d8e2f56a78a6a58da3c809c46b1da0f9d2c71a3","accepted_R45_blend":"224131c7adc928d5d6f0377d030d5a350c59b8664c13303a2731d6dfc6e9a722","standalone_R46_seat_blend":"e84c723111f8409686ee2d4e953c021212a76055bcb24ba0aad8138ebae828a4","standalone_R47_gauge_blend":"7367034bf9900e380f0f61d8d89c19322e8d22207dcba6c5124bf8f572803c28"}
TASK="FERRARI16-SLOTA-DAYTONA-CROSSQA-NATIVE-INTEGRATION-GUARD-20261109-V4"
def sha(p):
    d=hashlib.sha256()
    with p.open("rb") as f:
        for ch in iter(lambda:f.read(1024*1024),b""):d.update(ch)
    return d.hexdigest()
def must(ok,msg):
    if not ok:raise RuntimeError("BLOCKED: "+msg)
def main():
    q=json.loads(QUEUE.read_text(encoding="utf-8"))
    w=json.loads(WORK.read_text(encoding="utf-8"))
    must(q["active_by_slot"]["A"]=="daytona365" and w["car_id"]=="daytona365" and w["slot"]=="A","wrong active vehicle")
    must(w["current_component"]=="cross_cockpit_qa" and w["dispatches_on_component"]==1,"component/budget not 1/2")
    must(w["components"]["cross_cockpit_qa"]["status"]=="IN_PROGRESS","cross QA not active")
    must(w["latest_accepted_editable_blend_sha256"]==EXPECTED["accepted_R45_blend"],"accepted R45 lineage moved")
    for k,p in SOURCES.items():must(sha(p)==EXPECTED[k],"provenance SHA mismatch "+k)
    records={name:json.loads((DEST/("probe_"+name+".json")).read_text(encoding="utf-8")) for name in ("ORIGINAL","R45","R46","R47")}
    must(records["ORIGINAL"]["source_sha256"]==EXPECTED["original_import_blend"],"original Blender probe mismatch")
    for k,tag in (("R45","accepted_R45_blend"),("R46","standalone_R46_seat_blend"),("R47","standalone_R47_gauge_blend")):
        must(records[k]["source_sha256"]==EXPECTED[tag],"probe file mismatch "+k)
    original=records["ORIGINAL"]["native_objects"]
    changed={}
    target_objects={"R46":"object00_group01_material017_a0","R47":"object00_group01_material015_a0"}
    for name in ("R46","R47"):
        native=records[name]["native_objects"]
        must(original.keys()==native.keys(),"original object inventory changed "+name)
        differences=sorted(k for k in original if native[k]["mesh_sha256"]!=original[k]["mesh_sha256"])
        must(differences==[target_objects[name]],"other native PMT object changed "+name+":"+repr(differences))
        must(all(original[k]["vertex_count"]==native[k]["vertex_count"] and original[k]["face_count"]==native[k]["face_count"] and original[k]["matrix_world"]==native[k]["matrix_world"] for k in original),"topology or transform changed "+name)
        changed[name]=differences
    r45=records["R45"]
    must(r45["all_mesh_count"]==113 and len(r45["native_objects"])==0,"R45 identity findings require reevaluation")
    must(not any(target_objects[name] in r45["target_related"] for name in target_objects),"unexpected native objects")
    # R45 uses a different, bespoke 113-object namespace. Importing un-mapped
    # full original native submeshes would duplicate/collide with existing seats/gauges.
    # Therefore do NOT write a new .blend or falsely report a merge.
    manifest={
        "schema_version":1,"task_id":TASK,"slot":"A","car_id":"daytona365","requested_component":"cross_cockpit_qa",
        "result":"BLOCKED_SAFE_NATIVE_OBJECT_MAP","wait_state":"WAITING_QA_INPUT","dispatch":"2/2",
        "hard_24h_geometry_stop":"ENFORCED","whole_vehicle_qa_pass":False,
        "source_mesh_changed":False,"changed_native_vertices_this_dispatch":0,
        "integrated_into_accepted_scene":False,"new_blend_saved":False,
        "new_blend_independent_reopen":"NOT_APPLICABLE_NO_NEW_BLEND",
        "existing_blends_independently_opened_by_official_blender_4_5_15":True,
        "same_driver_camera_render":"EXISTING_R45_OBSERVATION_1434_ONLY; NO_NEW_AFTER_MERGE_RENDER",
        "matched_authentic_photo_driver_eye":"NOT_PASS_CAMERA_UNCALIBRATED",
        "source_sha256":EXPECTED,
        "current_input_sha256":EXPECTED["accepted_R45_blend"],
        "current_output_sha256":EXPECTED["accepted_R45_blend"],
        "input_equals_output":True,
        "public_native_original_objects_r46_r47":changed,
        "r45_visible_mesh_objects":113,"r45_matching_original_named_native_objects":0,
        "r46_r47_native_original_mesh_count":len(original),
        "safe_replacement_mapping":"NOT_PROVEN",
        "blocking_reason":"R45 has 113 source-derived specialized meshes but neither original PMT015 nor PMT017 native object identity; blindly appending R46/R47 30-object source scenes or swapping whole native submeshes risks duplicate overlapping seats/gauges and unrelated geometry.",
        "next_step":"PARK_SLOT_A_WAITING_QA_INPUT; require explicit verified one-to-one R45 seat/gauge source-object vertex mapping; never return to P0 micro-polish",
        "private_reference_photos_on_n100":[
            {"name":"ADD_interior_LHD.jpg","sha256":"6eae2fafd6369c1dbd4b82df8e24834d2d284bc3415cace15a9ea830cadd26eb"},
            {"name":"REF2_dashboard_original_e91527ff82f3.jpg","sha256":"6c87cd360497eead51a8aba83c6c4e07986247c47f4dbd5a181fcecf81a1f004"}],
        "original_game_pmt_bytes_published":False,"private_photo_bytes_published":False,
        "aes_or_secret_used":False,"pmto_vc_ovc3_game_exported":False,
        "dashboard_steering_glass_other_slot_changed":False,
        "artifacts":{"probe_source_script":"probe_native_sources.py","probes":["probe_ORIGINAL.json","probe_R45.json","probe_R46.json","probe_R47.json"],
                     "audit_script":"publish_blocked_qa.py"},
        "score_delta":0
    }
    manifest["artifact_sha256"]={p.name:sha(p) for p in [DEST/"probe_native_sources.py",DEST/"publish_blocked_qa.py"]+[DEST/("probe_"+k+".json") for k in ("ORIGINAL","R45","R46","R47")]}
    qa="""# Daytona365 SLOT A cross_cockpit_qa V4 integration guard

**BLOCKED_SAFE_NATIVE_OBJECT_MAP / WAITING_QA_INPUT / turn 2 of 2. Vehicle QA NOT PASS.**

- Native resource SHA: `%s`; original imported Blender SHA: `%s`.
- R45 accepted editable Blender SHA (input = output, unchanged): `%s`. 113 existing meshes, five saved camera objects; **zero** original source native object IDs named `object...`.
- R46 native PMT017 seat source SHA `%s`: compared to original import, **only** `object00_group01_material017_a0` changed; all original object counts, topology counts and transforms preserved.
- R47 native PMT015 instrument source SHA `%s`: compared to original import, **only** `object00_group01_material015_a0` changed; all original object counts, topology counts and transforms preserved.
- The R45 cabin already contains specialized seat and gauge structures but neither original PMT017 nor PMT015 object ID. Thus direct native-object replacement cannot be proven, and appending whole native objects could overlap existing cabin/alter unrelated geometry. **No speculative integration, no source mesh change, no invented model.**
- Blender 4.5.15 independently opened all four existing sources for this geometry inventory. There was **no newly saved .blend**, hence no new-blend independent reopen nor post-merge matched camera render. Previous R45 cross-cockpit observation remains available from the 14:34 QA checkpoint; private LHD photo references are not same-camera calibrated and remain on N100.
- All dashboards, steering, windshield/glass/A-pillars and SLOT C remain unchanged. No PMT/OVC/OVC3 exports, new textures, PBR, AES or secrets.
- **Next:** park SLOT A in `WAITING_QA_INPUT` until a verifiable original PMT017/PMT015-to-R45 object/vertex mapping exists. The 24h geometry cutoff and 2/2 dispatch cap are enforced. Do not auto-advance car or return to wheel/dashboard cosmetic edits.
"""%(EXPECTED["original_game_pmt"],EXPECTED["original_import_blend"],EXPECTED["accepted_R45_blend"],EXPECTED["standalone_R46_seat_blend"],EXPECTED["standalone_R47_gauge_blend"])
    part=w["components"]["cross_cockpit_qa"]
    part.update({"status":"BLOCKED","observation_status":"WAITING_QA_INPUT","blocking_reason":manifest["blocking_reason"],
        "dispatches_consumed_this_phase":2,"source_edits_this_phase":0,
        "native_source_edit":False,"integrated_into_accepted_scene":False,
        "input_blend_sha256":EXPECTED["accepted_R45_blend"],
        "output_blend_sha256":EXPECTED["accepted_R45_blend"],
        "last_saved_blend_sha256":None,
        "latest_qa_receipt":"artifacts/slot_A/daytona365/cross_cockpit_qa_v4_integration_20261109/manifest.json",
        "next":"WAITING_QA_INPUT",
        "remaining_blockers":["R45 no 1:1 PMT017/PMT015 native object mapping","exact original game driver-eye uncalibrated","seven same-camera authentic photo views incomplete","R46/R47 independent native objects not safely merged","existing source connectivity/unclosed surfaces"]})
    part.setdefault("evidence_refs",[]).extend([
         "artifacts/slot_A/daytona365/cross_cockpit_qa_v4_integration_20261109/manifest.json",
         "artifacts/slot_A/daytona365/cross_cockpit_qa_v4_integration_20261109/QA.md"])
    w["dispatches_on_component"]=2
    w["current_component"]="cross_cockpit_qa"
    w["slot_wait_state"]="WAITING_QA_INPUT"
    w["last_dispatch_attempt"]={
       "task_id":TASK,"component":"cross_cockpit_qa","result":"BLOCKED_SAFE_NATIVE_OBJECT_MAP",
       "valid_controller_dispatch_consumed":1,"component_budget_now":"2/2",
       "geometry_changed":False,"integrated_into_accepted_scene":False,
       "input_sha256":EXPECTED["accepted_R45_blend"],
       "output_sha256":EXPECTED["accepted_R45_blend"],
       "next":"WAITING_QA_INPUT","full_vehicle_qa_pass":False}
    w["notes"]="SLOT A 24h cutoff: cross_cockpit_qa 2/2 BLOCKED original PMT017/015 native object identity absent in 113-mesh R45 scene; no unsafe merge/new .blend. WAITING_QA_INPUT, NOT car QA PASS."
    (DEST/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (DEST/"QA.md").write_text(qa,encoding="utf-8")
    WORK.write_text(json.dumps(w,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BLOCKED_SAFE_NATIVE_OBJECT_MAP: saved QA manifest + workpack; R45 unchanged; slot A waiting; zero new .blend")
if __name__=="__main__":main()