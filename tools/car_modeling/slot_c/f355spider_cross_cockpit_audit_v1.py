#!/usr/bin/env python3
"""F355 Spider SLOT C cross-cockpit QA: do not modify .blend."""
from pathlib import Path
import json,csv,hashlib,struct,subprocess,sys
ROOT=Path("/home/chatgpt-runner/imsi1_slotC_steering_head_20261110")
BLENDER=Path("/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender")
PMT=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f355sp_pmt.sz")
PHOTOS=Path("/home/chatgpt-runner/outrun2_vr_refs/20261104_16car_cockpit/COVERAGE_MATRIX_16x8.csv")
QUE=ROOT/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json"
WP=ROOT/"docs/automation/FERRARI_COCKPIT_WORKPACK_C_F355SPIDER.json"
OUT=ROOT/"artifacts/slot_C/f355spider/cross_cockpit_qa_v1"
TASK="FERRARI16-SLOTC-F355SPIDER-CROSS-COCKPIT-QA-V1-20261110"
PARTS=["center_console","visible_seat","instrument_cluster","dashboard","steering_wheel"]
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def scan(tag):
 import bpy
 from mathutils import Vector
 scene=bpy.context.scene
 objs={o.name:o for o in bpy.data.objects if o.type=="MESH"}
 assert len(objs)==96 and all(x.startswith("PMT_F355SPIDER_") for x in objs)
 res={}
 for name,o in sorted(objs.items()):
  m=o.data;h=hashlib.sha256();t=hashlib.sha256();uv=hashlib.sha256()
  for v in m.vertices:h.update(struct.pack("<3d",*map(float,v.co)))
  for p in m.polygons:
   t.update(struct.pack("<I",len(p.vertices)))
   for idx in p.vertices:t.update(struct.pack("<I",int(idx)))
  for layer in m.uv_layers:
   for item in layer.data:uv.update(struct.pack("<2f",*map(float,item.uv)))
  x=struct.pack("<16d",*(float(v) for row in o.matrix_world for v in row))
  res[name]={"coords":h.hexdigest(),"topology":t.hexdigest(),"uv":uv.hexdigest(),
   "transform":hashlib.sha256(x).hexdigest(),"vertices":len(m.vertices),
   "faces":len(m.polygons),"modifiers":len(o.modifiers),"parent":bool(o.parent)}
 # Identical source-space camera from previous F355 instrument-context QA;
 # NOT an original-game camera; glass and steering overlays excluded.
 cd=bpy.data.cameras.new("TEMP_NATIVE_QA_CAMERA")
 c=bpy.data.objects.new("TEMP_NATIVE_QA_CAMERA",cd);scene.collection.objects.link(c)
 cam_before=scene.camera
 rend=(scene.render.engine,scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath)
 hide={n:o.hide_render for n,o in objs.items()}
 try:
  cd.type="ORTHO";cd.ortho_scale=1.2;c.location=(-.54,1.0,.28)
  c.rotation_euler=(Vector((-.35,.73,-.66))-c.location).to_track_quat("-Z","Y").to_euler()
  scene.camera=c;scene.render.engine="BLENDER_WORKBENCH"
  scene.render.resolution_x=1100;scene.render.resolution_y=760
  scene.render.filepath=str(OUT/("native_context_"+tag+".png"))
  for n,o in objs.items():o.hide_render=not n.startswith("PMT_F355SPIDER_object00_group01_")
  bpy.ops.render.render(write_still=True)
 finally:
  scene.camera=cam_before
  scene.render.engine,scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath=rend
  for n,o in objs.items():o.hide_render=hide[n]
  bpy.data.objects.remove(c,do_unlink=True);bpy.data.cameras.remove(cd,do_unlink=True)
 data={"mesh_count":len(res),"blend_sha256":sha(bpy.data.filepath),"meshes":res}
 (OUT/("scan_"+tag+".json")).write_text(json.dumps(data,indent=2)+"\n")
 print("BLENDER_INDEPENDENT_SCAN_PASS",tag,len(res),flush=True)
def driver():
 q=json.loads(QUE.read_text());w=json.loads(WP.read_text())
 assert q["active_by_slot"]["C"]=="f355spider" and w["car_id"]=="f355spider" and w["slot"]=="C"
 assert w["current_component"]=="cross_cockpit_qa" and w["components"]["cross_cockpit_qa"]["status"]=="NOT_STARTED"
 assert not w["full_vehicle_qa_pass"]
 assert sha(PMT)==w["original_game_resource_sha256"]
 base=ROOT/w["original_import_blend_file"];cur=ROOT/w["latest_accepted_editable_blend_file"]
 assert sha(base)==w["original_import_blend_sha256"]
 assert sha(cur)==w["latest_accepted_editable_blend_sha256"]
 previous=sha(base);expected=set();chain=[]
 for comp in PARTS:
  p=ROOT/("artifacts/slot_C/f355spider/"+comp+"_v1/receipt.json")
  r=json.loads(p.read_text())
  assert r["slot"]=="C" and r["vehicle"]=="f355spider" and r["component"]==comp
  assert r["input_sha256"]==previous,(comp,"source fork")
  output=ROOT/("artifacts/slot_C/f355spider/"+comp+"_v1/"+r["output_blend"])
  assert sha(output)==r["output_sha256"]
  previous=r["output_sha256"];expected.update(r["modified_objects"])
  chain.append({"component":comp,"receipt_sha256":sha(p),"source_blend":str(output.relative_to(ROOT)),"output_sha256":previous})
 assert previous==sha(cur)
 OUT.mkdir(parents=True,exist_ok=False)
 for tag,path in (("baseline",base),("accepted",cur)):
  p=subprocess.run([str(BLENDER),"-b",str(path),"-t","2","--python",str(Path(__file__).resolve()),"--",tag],capture_output=True,text=True,timeout=140)
  print(tag,p.returncode,p.stdout[-700:],p.stderr[-200:],flush=True)
  if p.returncode:raise RuntimeError("Blender independent scan failed")
 b=json.loads((OUT/"scan_baseline.json").read_text());a=json.loads((OUT/"scan_accepted.json").read_text())
 bm=b["meshes"];am=a["meshes"]
 assert len(bm)==len(am)==96 and bm.keys()==am.keys()
 edited=sorted(n for n in bm if bm[n]["coords"]!=am[n]["coords"])
 assert set(edited)==expected,{"changed":edited,"expected":sorted(expected)}
 for n in bm:
  for field in ("topology","uv","transform","vertices","faces","modifiers","parent"):
   assert bm[n][field]==am[n][field],(n,field)
 assert len(edited)==5
 with PHOTOS.open(newline="",encoding="utf8") as f:
  photos=[r for r in csv.DictReader(f) if r["vehicle"]=="F355 Spider"]
 assert len(photos)==8
 verified=[r["part"] for r in photos if r["qa_status"]=="PASS_VISUAL"]
 missing=[r["part"] for r in photos if r["qa_status"]!="PASS_VISUAL"]
 assert len(verified)==2 and "01_driver_eye" in missing
 from PIL import Image,ImageChops
 diff=ImageChops.difference(Image.open(OUT/"native_context_baseline.png").convert("RGB"),
                          Image.open(OUT/"native_context_accepted.png").convert("RGB"))
 bbox=diff.getbbox();diff.save(OUT/"native_context_delta.png")
 report={
 "task_id":TASK,"slot":"C","car_id":"f355spider","component":"cross_cockpit_qa",
 "status":"QA_WAITING_INPUT","new_geometry_change":False,"new_integrated_checkpoint":False,
 "existing_integrated_chain_verified":True,"chain":chain,
 "original_native_pmt_sha256":sha(PMT),"original_import_blend_sha256":sha(base),
 "accepted_integrated_blend_sha256":sha(cur),"accepted_integrated_blend":str(cur.relative_to(ROOT)),
 "independent_blender_reopen":"PASS_2_SEPARATE_BLENDER_PROCESSES",
 "native_mesh_count":96,"edited_original_objects":edited,"changed_mesh_count":5,"untouched_mesh_count":91,
 "all_other_meshes_including_protected_front_glass_unchanged":True,
 "all_mesh_topology_UV_transform_and_counts_unchanged":True,
 "same_camera_source_space_render_delta_bbox":bbox,
 "source_space_render_is_calibrated_driver_eye":False,"matched_driver_view":False,
 "private_photo_matrix_sha256":sha(PHOTOS),"photo_views_verified":verified,
 "photo_views_missing":missing,"photo_views_verified_count":2,"photo_views_required_count":8,
 "final_blockers":["Original-game seated driver camera not calibrated","Six authenticated photo-view categories not verified","Driver controls and inner door native attribution BLOCKED"],
 "whole_vehicle_qa_pass":False,"game_exports":[],"new_textures":[]}
 (OUT/"QA.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 (OUT/"QA.md").write_text(
 "# F355 Spider — SLOT C cross-cockpit native QA\n\n"
 "Status: QA_WAITING_INPUT, NOT a full-vehicle PASS. This is a one-time source audit, not a new mesh edit.\n\n"
 "Original PMT / initial import / accepted integrated .blend SHA256: "+sha(PMT)+" / "+sha(base)+" / "+sha(cur)+".\n\n"
 "Accepted chain: source import -> console -> seat -> cluster -> dashboard -> steering, all five receipt SHA links match.\n\n"
 "Independent Blender reopening of both native scenes: PASS, 96 original mesh identities; five allowed native objects changed and 91 fully unchanged, including front glass, A pillars and borders. Topology, UV, transforms and counts are invariant.\n\n"
 "Source-space two-render image is diagnostic only. Real OutRun camera eye and photo-registered matching are NOT verified.\n\n"
 "Photos: 2/8 views verified, six required views missing: "+", ".join(missing)+". Driver controls/inner door remain BLOCKED. No further same-input QA or P0 smoothing retry. No new .blend or mesh modification in this audit.\n")
 manifest={"schema_version":1,"task_id":TASK,"slot":"C","status":"QA_WAITING_INPUT",
 "native_pmt_sha256":sha(PMT),"original_blend_sha256":sha(base),"accepted_blend_sha256":sha(cur),
 "source_chain":chain,"files":{p.name:{"sha256":sha(p),"bytes":p.stat().st_size} for p in OUT.iterdir() if p.is_file()},
 "script":str(Path(__file__).relative_to(ROOT)),"script_sha256":sha(__file__),
 "encrypted":False,"parts_required":False,"private_photos_published":False,
 "whole_vehicle_qa_pass":False}
 (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
 c=w["components"]["cross_cockpit_qa"]
 c.update({"status":"QA_WAITING_INPUT","source_edits_this_phase":0,"dispatches_consumed_this_phase":0,
  "blocking_reason":"No calibrated game seated eye and 6/8 photo-view categories unverified; 2 native parts still BLOCKED.",
  "last_saved_blend_sha256":sha(cur),
  "evidence_refs":[str(p.relative_to(ROOT)) for p in OUT.iterdir() if p.is_file()]})
 w["known_final_qa_blockers"]=report["final_blockers"]
 w["full_vehicle_qa_pass"]=False
 w["notes"]="F355 native integrated five-part Blender chain independently audited: 96 objects, five modified/91 unchanged, windshield protected. QA_WAITING_INPUT, no calibrated driver eye, 2/8 verified photos; not vehicle PASS."
 WP.write_text(json.dumps(w,ensure_ascii=False,indent=2)+"\n")
 car=next(c for c in q["cars"] if c["id"]=="f355spider")
 assert car["slot"]=="C" and not car["whole_car_qa_pass"]
 car["notes"]=w["notes"]
 car["last_slot_c_cross_cockpit_qa"]={"task_id":TASK,"status":"QA_WAITING_INPUT",
  "accepted_blend_sha256":sha(cur),"original_meshes":96,"untouched_meshes":91,
  "photo_coverage":"2/8","driver_eye_calibrated":False,"whole_car_qa_pass":False,
  "manifest":str((OUT/"manifest.json").relative_to(ROOT))}
 QUE.write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\n")
 print("CROSS_COCKPIT_QA_VERIFIED",json.dumps({"edited":edited,"photos":verified,"bbox":bbox}),flush=True)
if __name__=="__main__":
 if "--" in sys.argv:scan(sys.argv[sys.argv.index("--")+1])
 else:driver()