#!/usr/bin/env python3
"""Finalize original PMT 360 Spider instrument_cluster first pass ONLY after native geometry + independent reopen."""
from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageDraw,ImageFont,ImageChops
R=Path(__file__).resolve().parents[2]
D=R/"artifacts/slot_A/360spider/instrument_cluster_20261110"
WP=R/"docs/automation/FERRARI_COCKPIT_WORKPACK_A_360SPIDER.json"
RE=D/"receipt.json"; O=D/"Ferrari360Spider_InstrumentCluster_OriginalPMT_R03.blend"
S=R/"artifacts/slot_A/360spider/visible_seat_20261110/Ferrari360Spider_VisibleSeat_OriginalPMT_R02.blend"
P=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_360sp_pmt.sz")
ORIGINAL="a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6"
BASE="b4f1d071119693172bbf786809da62dce8acb0c84e52d9779a6b1a996654ce57"
INPUT="af5a9a9d9650d261b1b24f56e5ff8b5291773e033c43087e000276940fbc87a2"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
q=json.loads((R/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json").read_text())
w=json.loads(WP.read_text());rec=json.loads(RE.read_text())
assert q["active_by_slot"]["A"]==w["car_id"]=="360spider"
assert w["current_component"]=="instrument_cluster" and w["dispatches_on_component"]==0
assert w["components"]["instrument_cluster"]["status"]=="NOT_STARTED"
assert w["latest_accepted_editable_blend_sha256"]==INPUT
assert sha(S)==INPUT and sha(P)==ORIGINAL
assert rec["status"]=="COVERED_PARTIAL_QA" and rec["independent_reopen"].startswith("PASS_")
assert rec["full_vehicle_qa_pass"] is False
assert sha(O)==rec["output_sha256"] and rec["input_sha256"]==INPUT
assert rec["native_original_pmt_sha256"]==ORIGINAL and rec["original_import_blend_sha256"]==BASE
assert rec["changed_existing_vertices"]==20 and rec["modified_objects"]==["PMT_object00_group01_material010_a0"]
assert len(rec["source_mesh_fingerprints_after"])==75
assert all(rec["source_mesh_fingerprints_before"][n]==rec["source_mesh_fingerprints_after"][n] for n in rec["source_mesh_fingerprints_before"] if n not in rec["modified_objects"])
assert rec["windshield_and_other_regions_untouched"] and rec["previous_console_seat_vertices_unchanged"]
# Images are same camera and same source original-derived faces; no real photo uploaded.
im1=Image.open(D/"instrument_seated_before.png").convert("RGB")
im2=Image.open(D/"instrument_seated_after.png").convert("RGB")
assert im1.size==im2.size
canvas=Image.new("RGB",(im1.width*2,im1.height+58),(15,15,15))
canvas.paste(im1,(0,58));canvas.paste(im2,(im1.width,58))
draw=ImageDraw.Draw(canvas)
draw.text((20,17),"BEFORE: accepted R02 native PMT",fill="white")
draw.text((im1.width+20,17),"AFTER: original PMT cluster hood R03",fill="white")
comp=D/"comparison_instrument_seated_before_after.jpg"
canvas.save(comp,quality=94,subsampling=0)
difference=ImageChops.difference(im1,im2)
box=difference.getbbox()
assert box is not None,"same-camera image unchanged; do not accept geometry-only fake"
# useful QA only, not a model acceptance substitute
nchange=sum(1 for r,g,b in difference.getdata() if max(r,g,b)>4)
qa={
 "slot":"A","car":"360spider","component":"instrument_cluster",
 "status":"COVERED_PARTIAL_QA","full_vehicle_qa_pass":False,
 "material_geometry_change_proved":True,
 "genuine_original_pmt_sha256":ORIGINAL,
 "baseline_import_blend_sha256":BASE,
 "accepted_input_sha256":INPUT,"output_sha256":rec["output_sha256"],
 "native_mesh_modified":"PMT_object00_group01_material010_a0",
 "changed_existing_vertices":20,"unchanged_native_objects":74,
 "noncluster_native_indices_unchanged":True,
 "previous_accepted_console_seat_indices_unchanged":True,
 "original_transforms_topology_faces_unchanged":True,
 "protected_windshield_frame_A_pillars_seals_untouched":True,
 "independent_blender_reopen":"PASS",
 "workspace_guard_verify_receipt":"PASS",
 "new_meshes":0,"new_textures":0,"exports":[],
 "compared_original_real_photo":"N100-only private 01_interior.jpg, silhouette reference",
 "matched_real_photo_registration":"NOT_CALIBRATED",
 "full_driver_eye_qa":"NOT_PASS",
 "render_comparison":{"same_camera":True,"different_RGB_pixels_threshold4":nchange,"image_width":im1.width,"image_height":im1.height,"difference_bbox":list(box)},
 "next_component":"dashboard",
 "notes":"Existing disjoint native cluster hood/binnacle islands sculpted: brow elevation up to 20 mm, recessed inner face up to 32 mm. No new gauges created; low-poly original unchanged in unrelated areas."
}
(D/"QA.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n")
(D/"QA.md").write_text(f"""# Ferrari 360 Spider / SLOT A / instrument_cluster R03
Status: **COVERED_PARTIAL_QA**, **NOT** vehicle QA PASS. Unique material geometry checkpoint, not doc-only.
- Original game PMT SHA256: `{ORIGINAL}` (remains N100).
- Native source import SHA256: `{BASE}`.
- Accepted input (seat R02) SHA256: `{INPUT}`.
- Output Blender R03 SHA256: `{rec["output_sha256"]}`.
- Existing PMT mesh: `PMT_object00_group01_material010_a0`, 20 existing vertices; native 5-island cluster face/hood only.
- Shape: existing gauge binnacle eyebrow +20 mm and instrument face recess up to 32 mm, no added gauge models, objects, vertices, faces, UV, textures or PBR.
- Fresh Blender 4.5.15 independent reopen PASS; original native mesh inventory 75; other 74 untouched. Previous seat/console vertex edits preserved.
- Protected windshield, A pillars, borders, seals, external/wheels unchanged.
- Same-camera original-derived ROI comparison render: `comparison_instrument_seated_before_after.jpg`. RGB pixels changed (>4): {nchange}. Render is proof of geometric appearance difference, not calibrated real-game QA.
- Private 360 Spider interior photo `04_360_Spider/01_interior.jpg` inspected as silhouette reference only (not uploaded). Exact driver-eye/photo registration remains outstanding.
- **Next component**: `dashboard` (new-car first pass only; no prior wheel or dash polish). Whole-car QA remains **NOT_PASS**.
""")
manifest={
 "schema":"ferrari16_plaintext_geometry_artifact_v1","slot":"A","vehicle":"360spider","component":"instrument_cluster",
 "original_native_pmt_on_n100":str(P),"original_native_pmt_sha256":ORIGINAL,
 "original_import_blend":str((R/"artifacts/slot_A/360spider/source_bootstrap/Ferrari360Spider_OriginalPMT_EditableBaseline.blend").relative_to(R)),
 "original_import_sha256":BASE,
 "input_blend":str(S.relative_to(R)),"input_sha256":INPUT,
 "output_blend":str(O.relative_to(R)),"output_sha256":rec["output_sha256"],
 "changed_original_vertices":20,"changed_original_meshes":rec["modified_objects"],
 "independent_reopen":"PASS","workspace_guard":"PASS","whole_vehicle_qa_pass":False,
 "binary_encoding":"plaintext direct .blend (no parts required; 467 kB)",
 "private_photos_uploaded":False,"artifacts":{}
}
for file in ["receipt.json","QA.json","QA.md","comparison_instrument_seated_before_after.jpg",
 "instrument_seated_before.png","instrument_seated_after.png","instrument_reverse_before.png",
 "instrument_reverse_after.png","instrument_overhead_before.png","instrument_overhead_after.png",
 "native_islands.json","native_object_bounds.json"]:
 path=D/file; assert path.is_file();manifest["artifacts"][file]={"sha256":sha(path),"size_bytes":path.stat().st_size}
for file in ["tools/car_modeling/source_edit_instrument_360spider.py",
 "tools/car_modeling/probe_instrument_360spider.py",
 "tools/car_modeling/instrument_island_visual_probe_360spider.py",
 "tools/car_modeling/render_instrument_probe_360spider.py"]:
 path=R/file;assert path.is_file();manifest["artifacts"][file]={"sha256":sha(path),"size_bytes":path.stat().st_size}
(D/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
component=w["components"]["instrument_cluster"]
component.update({
 "status":"COVERED_PARTIAL_QA","source_edits_this_phase":1,"dispatches_consumed_this_phase":1,
 "evidence_refs":[str((D/f).relative_to(R)) for f in ["receipt.json","QA.json","QA.md","manifest.json",
 "Ferrari360Spider_InstrumentCluster_OriginalPMT_R03.blend",
 "comparison_instrument_seated_before_after.jpg",
 "instrument_seated_before.png","instrument_seated_after.png"]] +
 ["tools/car_modeling/source_edit_instrument_360spider.py"],
 "last_saved_blend_sha256":rec["output_sha256"],
 "qa_gate":"NATIVE_SOURCE_20_VERTEX_GEOMETRY_AND_INDEPENDENT_BLENDER_REOPEN_PASS; REAL_PHOTO_DRIVER_EYE_QA_PENDING",
 "modified_original_mesh":"PMT_object00_group01_material010_a0","native_vertices_changed":20,
 "unchanged_original_meshes":74,"previous_console_seat_vertices_unchanged":True,
 "protected_regions_untouched":True
})
w["latest_accepted_editable_blend_sha256"]=rec["output_sha256"]
w["latest_accepted_editable_blend_file"]=str(O.relative_to(R))
w["current_component"]="dashboard";w["dispatches_on_component"]=0
w["last_material_task_id"]="FERRARI16-SLOTA-360SPIDER-NATIVE-INSTRUMENT-R03-20261110-"+rec["output_sha256"][:8].upper()
w["notes"]=("2026-11-10 instrument_cluster: 20 existing original PMT binnacle vertices changed, original 74 other meshes and prior console/seat vertices preserved, independent Blender reopen + guard PASS; PARTIAL_QA, not vehicle PASS. Next dashboard. "+w["notes"])[:8000]
assert w["components"]["dashboard"]["status"]=="NOT_STARTED"
assert not w["full_vehicle_qa_pass"]
WP.write_text(json.dumps(w,indent=2,ensure_ascii=False)+"\n")
print("FINALIZE_SUCCESS",json.dumps({"task_id":w["last_material_task_id"],"output_sha256":rec["output_sha256"],"nchange_rgb":nchange,"status":component["status"],"next":w["current_component"]}),flush=True)
