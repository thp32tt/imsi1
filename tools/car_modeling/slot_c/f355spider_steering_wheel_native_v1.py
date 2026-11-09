#!/usr/bin/env python3
"""F355 Spider Slot C native PMT steering wheel ONE first-pass shape edit.
Only pre-existing source object22_group00_material001_a0 vertices are changed.
No new meshes/materials/textures and no windshield or exterior changes.
"""
import sys, json, math, hashlib, struct, subprocess
from pathlib import Path

ROOT=Path("/home/chatgpt-runner/imsi1_slotC_steering_20261110")
BLENDER=Path("/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender")
PMT=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f355sp_pmt.sz")
PHOTO=Path("/home/chatgpt-runner/outrun2_vr_refs/20261104_16car_cockpit/05_F355_Spider/01_interior.jpg")
IN=ROOT/"artifacts/slot_C/f355spider/dashboard_v1/F355Spider_OriginalPMT_Dashboard_CenterVent_Facia_v1.blend"
BASE=ROOT/"artifacts/slot_C/f355spider/source_bootstrap/F355Spider_OriginalPMT_SourceBaseline_v1.blend"
DIR=ROOT/"artifacts/slot_C/f355spider/steering_wheel_v1"
OUT=DIR/"F355Spider_OriginalPMT_Steering_ThreeSpoke_v1.blend"
RECEIPT=DIR/"receipt.json"
TARGET="PMT_F355SPIDER_object22_group00_material001_a0"
EMBLEM="PMT_F355SPIDER_object22_group00_material000_a0"
PMT_SHA="d9af341653ef44371e8df2efc4024af92d7ca03665acef04a4c3c65200bb7b11"
BASE_SHA="4fa9bdc314c5e30ab890adcff160377436540646588a36f1c4c1649c5df7186e"
IN_SHA="8734757c3bac3938c8313214720c7d9e9b5d42fdb7095001de9fd90471d93c0d"
TASK="FERRARI16-SLOTC-F355SPIDER-STEERING-WHEEL-NATIVE-PMT22-V1-20261110"
sys.path.insert(0,str(ROOT/"tools/car_modeling"))
from workspace_guard import preflight, verify_receipt

def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for data in iter(lambda:f.read(1048576),b""):h.update(data)
 return h.hexdigest()

def gate():
 q=json.loads((ROOT/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json").read_text())
 w=json.loads((ROOT/"docs/automation/FERRARI_COCKPIT_WORKPACK_C_F355SPIDER.json").read_text())
 assert q["active_by_slot"]["C"]=="f355spider" and w["car_id"]=="f355spider" and w["slot"]=="C"
 assert w["current_component"]=="steering_wheel" and w["dispatches_on_component"]==0
 assert w["components"]["steering_wheel"]["status"]=="NOT_STARTED"
 assert w["latest_accepted_editable_blend_sha256"]==IN_SHA
 assert preflight(q,w,"C","steering_wheel")=="PASS C/f355spider target=steering_wheel turn=1/2"
 for p,h in [(PMT,PMT_SHA),(BASE,BASE_SHA),(IN,IN_SHA)]:assert p.exists() and sha(p)==h,(p,sha(p) if p.exists() else "MISSING")
 assert PHOTO.is_file() and BLENDER.is_file()
 return q,w

def signature(o):
 m=o.data;h=hashlib.sha256()
 h.update(o.name.encode());h.update(struct.pack("<16d",*(float(x) for row in o.matrix_world for x in row)))
 h.update(struct.pack("<QQ",len(m.vertices),len(m.polygons)))
 for v in m.vertices:h.update(struct.pack("<3d",*map(float,v.co)))
 for face in m.polygons:
  h.update(struct.pack("<I",len(face.vertices)))
  for i in face.vertices:h.update(struct.pack("<I",int(i)))
 assert len(m.uv_layers)==1 and m.attributes.get("PMT_NATIVE_NORMAL")
 for t in m.uv_layers[0].data:h.update(struct.pack("<2f",*map(float,t.uv)))
 for v in m.attributes["PMT_NATIVE_NORMAL"].data:h.update(struct.pack("<3f",*map(float,v.vector)))
 return h.hexdigest()

def get_meshes():
 import bpy
 meshes={o.name:o for o in bpy.data.objects if o.type=="MESH"}
 assert len(meshes)==96 and set([TARGET,EMBLEM]).issubset(meshes)
 m=meshes[TARGET].data
 assert len(m.vertices)==293 and len(m.polygons)==368
 assert len(meshes[EMBLEM].data.vertices)==4
 for o in meshes.values():
  assert o.name.startswith("PMT_F355SPIDER_")
  assert not o.modifiers and not o.constraints and not o.parent
  assert all(abs(float(v))<1e-7 for v in o.location)
  assert all(abs(float(v))<1e-7 for v in o.rotation_euler)
  assert all(abs(float(v)-1)<1e-7 for v in o.scale)
 return meshes

def smoothstep(x):
 t=max(0.,min(1.,x))
 return t*t*(3-2*t)

def sculpt(o):
 """Refine the *existing* lower pair of native wheel spokes toward the
 real F355 Spider's narrower central lower stem; slightly compact the
 lower airbag/pad corners. Keep rim anchors, badge, topology and UV intact.
 """
 from mathutils import Vector
 verts=o.data.vertices
 old=[v.co.copy() for v in verts]
 # Explicit native face islands from original PMT wheel, NOT new synthetic geo.
 lower=set(list(range(132,183))+list(range(186,220))+list(range(241,247))+[264,265,274])
 panel=set(list(range(247,264))+[266,275,292])
 edits=[]
 for i,v in enumerate(verts):
  x,y,z=map(float,old[i])
  dx=dy=0.
  r=math.hypot(x,y)
  if i in lower and y<-.091 and abs(x)>.006 and abs(x)<.108:
   radial=smoothstep((.171-r)/.042)
   vertical=smoothstep((-y-.083)/.050)
   dx=-math.copysign(.029*radial*vertical,x)
   # move only inner lower spokes. Original outer/rim anchors stay anchored.
  elif i in panel and y<-.055 and abs(x)>.018:
   taper=smoothstep((-y-.05)/.05)
   dx=-math.copysign(.011*taper,x)
   dy=-.009*taper
  if abs(dx)+abs(dy)>1e-8:
   v.co=Vector((x+dx,y+dy,z))
   edits.append({"index":i,"old_xyz":[round(x,7),round(y,7),round(z,7)],
                 "new_xyz":[round(x+dx,7),round(y+dy,7),round(z,7)],
                 "delta_xyz":[round(dx,7),round(dy,7),0],
                 "displacement_m":math.hypot(dx,dy)})
 o.data.update()
 assert 18<=len(edits)<=100,len(edits)
 assert max(e["displacement_m"] for e in edits)>.008
 assert max(e["displacement_m"] for e in edits)<.032
 assert all((old[i]-verts[i].co).length<1e-8 for i in range(len(verts)) if i not in {e["index"] for e in edits})
 # Preserve original mesh topology; reject flipped faces from aggressive deformation.
 def normal(a,b,c):return (b-a).cross(c-a)
 for p in o.data.polygons:
  if len(p.vertices)!=3:continue
  ids=list(p.vertices)
  before=normal(*(old[i] for i in ids))
  after=normal(*(verts[i].co for i in ids))
  if before.length>1e-9: assert after.length>before.length*.15 and before.dot(after)>0,(ids,before,after)
 return edits

def render(path,meshes):
 import bpy
 from mathutils import Vector
 sc=bpy.context.scene
 prev_cam=sc.camera
 prev_engine=sc.render.engine
 prev_res=(sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage,sc.render.filepath,sc.render.image_settings.file_format)
 old_vis={n:(o.hide_render,tuple(o.color)) for n,o in meshes.items()}
 camdata=bpy.data.cameras.new("TEMP_F355_NATIVE_WHEEL_QA")
 cam=bpy.data.objects.new("TEMP_F355_NATIVE_WHEEL_QA",camdata);sc.collection.objects.link(cam)
 try:
  sc.camera=cam;camdata.type="ORTHO";camdata.ortho_scale=.43
  cam.location=(0,0,1);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat("-Z","Y").to_euler()
  sc.render.engine="BLENDER_WORKBENCH"
  sc.render.resolution_x=1100;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
  sc.display.shading.light="STUDIO";sc.display.shading.color_type="OBJECT";sc.display.shading.show_cavity=True
  sc.render.image_settings.file_format="PNG";sc.render.filepath=str(path)
  for n,o in meshes.items():
   o.hide_render=n not in (TARGET,EMBLEM)
   o.color=(.18,.19,.21,1) if n==TARGET else (.74,.65,.38,1)
  bpy.ops.render.render(write_still=True)
 finally:
  for n,o in meshes.items():o.hide_render,o.color=old_vis[n]
  sc.camera=prev_cam;sc.render.engine=prev_engine
  (sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage,sc.render.filepath,sc.render.image_settings.file_format)=prev_res
  bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camdata,do_unlink=True)
 return sha(path)

def edit():
 import bpy
 gate()
 assert Path(bpy.data.filepath).resolve()==IN.resolve()
 assert not OUT.exists() and not RECEIPT.exists()
 DIR.mkdir(parents=True,exist_ok=True)
 meshes=get_meshes()
 before={n:signature(o) for n,o in meshes.items()}
 counts={n:(len(o.data.vertices),len(o.data.polygons)) for n,o in meshes.items()}
 before_render=render(DIR/"wheel_before.png",meshes)
 assert before=={n:signature(o) for n,o in meshes.items()}
 moves=sculpt(meshes[TARGET])
 after={n:signature(o) for n,o in meshes.items()}
 assert sorted(k for k in meshes if after[k]!=before[k])==[TARGET]
 assert all(counts[n]==(len(o.data.vertices),len(o.data.polygons)) for n,o in meshes.items())
 after_render=render(DIR/"wheel_after.png",meshes)
 assert after=={n:signature(o) for n,o in meshes.items()}
 bpy.context.scene["f355spider_native_wheel_pass"]="PMT_OBJECT22_MATERIAL001_LOWER_SPOKE_SILHOUETTE"
 bpy.context.scene["whole_vehicle_qa_pass"]=False
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
 assert sha(PMT)==PMT_SHA and sha(BASE)==BASE_SHA and sha(IN)==IN_SHA
 rec={"task_id":TASK,"slot":"C","vehicle":"f355spider","component":"steering_wheel",
 "status":"COVERED_PARTIAL_QA","native_original_pmt_sha256":PMT_SHA,
 "original_import_blend_sha256":BASE_SHA,"input_blend":IN.name,"input_sha256":IN_SHA,
 "output_blend":OUT.name,"output_sha256":sha(OUT),"original_mesh":TARGET,
 "modified_objects":[TARGET],"source_mesh_fingerprints_before":before,"source_mesh_fingerprints_after":after,
 "unchanged_other_native_meshes":95,"changed_existing_vertices":len(moves),"per_vertex_geometry_deltas":moves,
 "max_vertex_displacement_m":max(e["displacement_m"] for e in moves),
 "windshield_and_other_regions_untouched":True,"protected_front_glass_untouched":True,
 "airbag_badge_original_mesh_untouched":True,"original_topology_and_UVs_unchanged":True,
 "real_photo_private":"05_F355_Spider/01_interior.jpg","real_photo_sha256":sha(PHOTO),
 "real_photo_comparison":"Qualitative original Ferrari F355 Spider lower single-spoke silhouette; not metric or seated-camera registered",
 "same_camera_wheel_before_sha256":before_render,"same_camera_wheel_after_sha256":after_render,
 "blender_saved":True,"independent_reopen":"PENDING",
 "full_vehicle_qa_pass":False,"next_component":"cross_cockpit_qa","exports":[],"new_textures":[]}
 RECEIPT.write_text(json.dumps(rec,indent=2,ensure_ascii=False)+"\n")
 print("STEERING_EDIT_SAVED",len(moves),sha(OUT),rec["max_vertex_displacement_m"],flush=True)

def reopen():
 import bpy
 gate()
 assert Path(bpy.data.filepath).resolve()==OUT.resolve()
 rec=json.loads(RECEIPT.read_text())
 assert sha(OUT)==rec["output_sha256"]
 meshes=get_meshes()
 sig={n:signature(o) for n,o in meshes.items()}
 assert sig==rec["source_mesh_fingerprints_after"]
 assert sorted(k for k in sig if sig[k]!=rec["source_mesh_fingerprints_before"][k])==[TARGET]
 assert bpy.context.scene["whole_vehicle_qa_pass"] is False
 assert bpy.context.scene["f355spider_native_wheel_pass"]=="PMT_OBJECT22_MATERIAL001_LOWER_SPOKE_SILHOUETTE"
 assert sha(PMT)==PMT_SHA and sha(BASE)==BASE_SHA and sha(IN)==IN_SHA
 rec["independent_reopen"]="PASS_BLENDER_4_5_15_SEPARATE_PROCESS"
 rec["independent_reopen_mesh_count"]=len(meshes)
 RECEIPT.write_text(json.dumps(rec,indent=2,ensure_ascii=False)+"\n")
 print("STEERING_INDEPENDENT_REOPEN_PASS",sha(OUT),flush=True)

def run_blender(action,source):
 cmd=[str(BLENDER),"-b",str(source),"--python",str(Path(__file__).resolve()),"--",action]
 print("RUN_BLENDER",action,flush=True)
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=150)
 print(r.stdout[-8000:],flush=True)
 if r.stderr:print("BLENDER_LOG",r.stderr[-1200:],flush=True)
 if r.returncode:raise RuntimeError("Blender failed "+str(r.returncode))

def finalize():
 q,w=gate()
 rec=json.loads(RECEIPT.read_text())
 assert verify_receipt(q,w,"C",rec,OUT).startswith("PASS")
 assert sha(PHOTO)==rec["real_photo_sha256"]
 assert sha(IN)==IN_SHA and sha(PMT)==PMT_SHA
 script=Path(__file__).resolve()
 from PIL import Image, ImageChops
 b=Image.open(DIR/"wheel_before.png").convert("RGB")
 a=Image.open(DIR/"wheel_after.png").convert("RGB")
 delta=ImageChops.difference(b,a)
 assert delta.getbbox() is not None,"wheel rendered image unchanged"
 delta.save(DIR/"wheel_delta.png")
 manifest={"schema_version":1,"task_id":TASK,"slot":"C","vehicle":"f355spider","component":"steering_wheel",
 "status":"COVERED_PARTIAL_QA","source_original_pmt_private":str(PMT),"source_original_pmt_sha256":PMT_SHA,
 "original_source_blend":str(BASE.relative_to(ROOT)),"original_source_blend_sha256":BASE_SHA,
 "input_blend":str(IN.relative_to(ROOT)),"input_sha256":IN_SHA,
 "output_blend":str(OUT.relative_to(ROOT)),"output_sha256":sha(OUT),"output_size_bytes":OUT.stat().st_size,
 "modified_original_native_object":TARGET,"changed_existing_vertices":rec["changed_existing_vertices"],
 "protected_objects_untouched":95,"source_script":str(script.relative_to(ROOT)),"source_script_sha256":sha(script),
 "receipt_sha256":sha(RECEIPT),"render_sha256":{p.name:sha(p) for p in sorted(DIR.glob("*.png"))},
 "private_photo_sha256":sha(PHOTO),"photo_comparison":"qualitative; not calibrated","independent_reopen":rec["independent_reopen"],
 "plaintext":True,"partition_required":OUT.stat().st_size>10*1024*1024,
 "original_pmt_uploaded":False,"private_photos_uploaded":False,"game_exports":[],"new_textures":[],
 "whole_vehicle_qa_pass":False,"next_component":"cross_cockpit_qa"}
 assert not manifest["partition_required"]
 (DIR/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
 qa={"task_id":TASK,"component":"steering_wheel","status":"COVERED_PARTIAL_QA",
 "source_mesh_changed":True,"source_native_identity":TARGET,"modified_existing_vertices":rec["changed_existing_vertices"],
 "maximum_displacement_m":rec["max_vertex_displacement_m"],
 "other_95_original_meshes_untouched":True,"original_source_PMT_untouched":True,"airbag_emblem_mesh_untouched":True,
 "glass_frame_A_pillar_untouched":True,"save_reopen":"PASS","photo_check":"QUALITATIVE_ONLY",
 "whole_car_qa":"NOT_PASS","next_component":"cross_cockpit_qa",
 "evidence":[str(p.relative_to(ROOT)) for p in [OUT,RECEIPT,DIR/"wheel_before.png",DIR/"wheel_after.png",DIR/"wheel_delta.png"]]}
 (DIR/"QA.json").write_text(json.dumps(qa,indent=2)+"\n")
 (DIR/"QA.md").write_text("# F355 Spider SLOT C steering wheel native first pass\n\n"
  "Original PMT object22 material001 wheel: adjusted only pre-existing lower spoke and lower airbag-pad vertices "
  "toward the narrower central lower-spoke silhouette in private original F355 Spider interior photograph. "
  "No new geometry or textures; no unrelated object moved. Same-camera before/after wheel renders included.\n\n"
  f"Changed vertices: {rec['changed_existing_vertices']}; maximum displacement {rec['max_vertex_displacement_m']:.5f} m. "
  "Other 95 native PMT meshes, emblem, front windshield and A-pillars unchanged by fingerprints. "
  "Original resource remains N100 only; independent Blender reopen and receipt guard PASS. "
  "Photo evidence is qualitative, not calibrated; full vehicle QA NOT PASS.\n")
 # Persist only after evidence proved. Never promote car to QA pass.
 ent=w["components"]["steering_wheel"]
 assert ent["source_edits_this_phase"]==0 and ent["dispatches_consumed_this_phase"]==0
 ent.update({"status":"COVERED_PARTIAL_QA","source_edits_this_phase":1,"dispatches_consumed_this_phase":1,
             "last_saved_blend_sha256":sha(OUT),"blocking_reason":None,
             "evidence_refs":[str(p.relative_to(ROOT)) for p in [OUT,RECEIPT,DIR/"manifest.json",DIR/"QA.json",DIR/"QA.md",DIR/"wheel_before.png",DIR/"wheel_after.png",DIR/"wheel_delta.png",script]]})
 w["latest_accepted_editable_blend_sha256"]=sha(OUT)
 w["latest_accepted_editable_blend_file"]=str(OUT.relative_to(ROOT))
 w["migration_input_blend_sha256"]=sha(OUT)
 w["migration_input_blend_file"]=str(OUT.relative_to(ROOT))
 w["last_material_component"]="steering_wheel"
 w["current_component"]="cross_cockpit_qa"
 w["dispatches_on_component"]=0
 w["full_vehicle_qa_pass"]=False
 w["notes"]="Original PMT object22 material001 steering wheel first-pass lower-spoke shape edited, other 95 native meshes unchanged; Blender separate reopen PASS, next cross_cockpit_qa; vehicle QA NOT PASS."
 (ROOT/"docs/automation/FERRARI_COCKPIT_WORKPACK_C_F355SPIDER.json").write_text(json.dumps(w,indent=2,ensure_ascii=False)+"\n")
 car=next(c for c in q["cars"] if c["id"]=="f355spider")
 assert car["slot"]=="C" and car["whole_car_qa_pass"] is False
 car["output_scene_sha256"]=sha(OUT)
 car["strategy_v3_next_component"]="cross_cockpit_qa"
 car["notes"]=w["notes"]
 car["last_slot_c_steering_wheel"]={
  "task_id":TASK,"component":"steering_wheel","status":"COVERED_PARTIAL_QA","native_mesh":TARGET,
  "modified_existing_vertices":rec["changed_existing_vertices"],"other_native_meshes_unchanged":95,
  "original_PMT_sha256":PMT_SHA,"input_sha256":IN_SHA,"output_sha256":sha(OUT),
  "reopen":"PASS","full_vehicle_qa_pass":False,"next":"cross_cockpit_qa",
  "manifest":str((DIR/"manifest.json").relative_to(ROOT))}
 (ROOT/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json").write_text(json.dumps(q,indent=2,ensure_ascii=False)+"\n")
 print("FINALIZED_NATIVE_WHEEL",json.dumps({"output_sha":sha(OUT),"edited":len(rec["per_vertex_geometry_deltas"]),"new_target":w["current_component"],"renders":manifest["render_sha256"]}),flush=True)

def main():
 action=(sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "driver")
 if action=="edit":edit()
 elif action=="reopen":reopen()
 elif action=="finalize":finalize()
 else:
  gate()
  run_blender("edit",IN)
  run_blender("reopen",OUT)
  finalize()
if __name__=="__main__":main()
