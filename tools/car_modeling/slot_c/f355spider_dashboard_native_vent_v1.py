#!/usr/bin/env python3
"""F355 Spider SLOT C dashboard: source-native center dash twin duct panel first pass.
Only eight existing source PMT019 vertices. Windshield/glass/frame/dash top untouched.
"""
import sys,os,math,struct,json,hashlib,subprocess
from pathlib import Path
ROOT=Path("/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-dashboard-20261110")
B=Path("/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender")
IN=ROOT/"artifacts/slot_C/f355spider/instrument_cluster_v1/F355Spider_OriginalPMT_InstrumentCluster_Visor_v1.blend"
BASE=ROOT/"artifacts/slot_C/f355spider/source_bootstrap/F355Spider_OriginalPMT_SourceBaseline_v1.blend"
PMT=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f355sp_pmt.sz")
PHOTO=Path("/home/chatgpt-runner/outrun2_vr_refs/20261104_16car_cockpit/05_F355_Spider/REF4_interior_03_f460291745.jpg")
OUT=ROOT/"artifacts/slot_C/f355spider/dashboard_v1"
OUTPUT=OUT/"F355Spider_OriginalPMT_Dashboard_CenterVent_Facia_v1.blend"
RC=OUT/"receipt.json"
PMT_SHA="d9af341653ef44371e8df2efc4024af92d7ca03665acef04a4c3c65200bb7b11"
BASE_SHA="4fa9bdc314c5e30ab890adcff160377436540646588a36f1c4c1649c5df7186e"
IN_SHA="ec320da62a7ac21bf88cef5ed205558f3542e03f6f35d6f76de5d4e3d7643e23"
TARGET="PMT_F355SPIDER_object00_group01_material019_a0"
PROTECTED=[
 "PMT_F355SPIDER_object00_group00_material004_a1",
 "PMT_F355SPIDER_object00_group01_material020_a0"
]
sys.path.insert(0,str(ROOT/"tools/car_modeling"))
from workspace_guard import preflight
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()
def gate():
 q=json.loads((ROOT/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json").read_text())
 w=json.loads((ROOT/"docs/automation/FERRARI_COCKPIT_WORKPACK_C_F355SPIDER.json").read_text())
 assert q["active_by_slot"]["C"]=="f355spider"
 assert w["car_id"]=="f355spider" and w["slot"]=="C"
 assert w["current_component"]=="dashboard" and w["dispatches_on_component"]==0
 assert w["components"]["dashboard"]["status"]=="NOT_STARTED"
 assert w["latest_accepted_editable_blend_sha256"]==IN_SHA
 assert preflight(q,w,"C","dashboard")=="PASS C/f355spider target=dashboard turn=1/2"
 for path,digest in [(PMT,PMT_SHA),(BASE,BASE_SHA),(IN,IN_SHA)]:
  assert path.exists() and sha(path)==digest,path
 assert PHOTO.is_file()
 return w
def sig(o):
 h=hashlib.sha256()
 h.update(o.name.encode());h.update(struct.pack("<16d",*(float(v) for row in o.matrix_world for v in row)))
 m=o.data;h.update(struct.pack("<QQ",len(m.vertices),len(m.polygons)))
 for v in m.vertices:h.update(struct.pack("<3d",*map(float,v.co)))
 for poly in m.polygons:
  h.update(struct.pack("<I",len(poly.vertices)))
  for j in poly.vertices:h.update(struct.pack("<I",int(j)))
 assert len(m.uv_layers)==1 and m.attributes.get("PMT_NATIVE_NORMAL")
 for u in m.uv_layers[0].data:h.update(struct.pack("<2f",*map(float,u.uv)))
 for n in m.attributes["PMT_NATIVE_NORMAL"].data:h.update(struct.pack("<3f",*map(float,n.vector)))
 return h.hexdigest()
def all_meshes():
 import bpy
 a={o.name:o for o in bpy.data.objects if o.type=="MESH"}
 assert len(a)==96 and TARGET in a and set(PROTECTED).issubset(a)
 assert len(a[TARGET].data.vertices)==16 and len(a[TARGET].data.polygons)==8
 for name,o in a.items():
  assert name.startswith("PMT_F355SPIDER_")
  assert not o.modifiers and not o.constraints and not o.parent
  assert max(abs(float(v)) for v in o.location)<1e-8
  assert max(abs(float(v)) for v in o.rotation_euler)<1e-8
  assert all(abs(float(v)-1)<1e-8 for v in o.scale)
 return a
def surface_clearance(target,mesh):
 lower=[]
 for i in range(8):
  p=target.data.vertices[i].co
  for name in PROTECTED:
   ok,near,normal,face=mesh[name].closest_point_on_mesh(p)
   assert ok
   lower.append(float((p-near).length))
 return min(lower)
def distort(target,mesh):
 # Hard source-native attribution: the 8 selected original vertices form two
 # disconnected central ventilation/dashboard fascia plates, each 4v/2tris.
 verts=target.data.vertices;old=[]
 for i in range(8):
  v=verts[i].co
  x,y,z=map(float,v)
  assert .007<=abs(x)<=.131 and .696<=y<=.743 and -.760<=z<=-.689,(i,x,y,z)
  old.append((x,y,z))
 assert surface_clearance(target,mesh)>.065,"not safely separated from original windshield surface"
 moved=[]
 for i in range(8):
  v=verts[i].co;x,y,z=old[i];side=-1 if x<0 else 1
  # Same real existing two vent panels; increase dash panel face height,
  # rear-facing projection and edge relief to give physical depth.
  dx=side*(.013 if abs(x)>.1 else .006)
  dy=.011 if y>.72 else -.020
  dz=.025 if y>.72 else .038
  v.x+=dx;v.y+=dy;v.z+=dz
  moved.append({"vertex":i,"original_xyz_m":[round(x,7),round(y,7),round(z,7)],"delta_m":[dx,dy,dz],"distance_m":math.sqrt(dx*dx+dy*dy+dz*dz)})
 assert len(moved)==8 and max(v["distance_m"] for v in moved)<.047
 target.data.update()
 clearance=surface_clearance(target,mesh)
 assert clearance>.065,"dashboard vent shape intersected protected windshield"
 return moved,clearance
def render(path,ms,zoom):
 import bpy
 from mathutils import Vector
 s=bpy.context.scene
 old_camera=s.camera
 old_r=(s.render.engine,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.filepath,s.render.image_settings.file_format)
 old_sh=(s.display.shading.light,s.display.shading.color_type,s.display.shading.show_cavity)
 old_o={k:(o.hide_render,tuple(o.color)) for k,o in ms.items()}
 data=bpy.data.cameras.new("TEMP_CENTER_DASH_QA")
 camera=bpy.data.objects.new("TEMP_CENTER_DASH_QA",data);s.collection.objects.link(camera)
 try:
  s.camera=camera;data.type="ORTHO";data.ortho_scale=.74 if zoom else 1.65
  camera.location=(0,1.00,.20) if zoom else (-.02,1.15,.55)
  camera.rotation_euler=(Vector((0,.735,-.75))-camera.location).to_track_quat("-Z","Y").to_euler()
  s.render.engine="BLENDER_WORKBENCH";s.render.resolution_x=1280;s.render.resolution_y=850;s.render.resolution_percentage=100
  s.display.shading.light="STUDIO";s.display.shading.color_type="OBJECT";s.display.shading.show_cavity=True
  s.render.image_settings.file_format="PNG";s.render.filepath=str(path)
  for name,o in ms.items():
   o.hide_render=name not in (TARGET,"PMT_F355SPIDER_object00_group01_material017_a0","PMT_F355SPIDER_object00_group01_material016_a0")
   o.color=(.18,.82,.45,1) if name==TARGET else (.68,.67,.67,1)
  bpy.ops.render.render(write_still=True)
 finally:
  for name,o in ms.items():o.hide_render,o.color=old_o[name]
  s.camera=old_camera
  (s.render.engine,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.filepath,s.render.image_settings.file_format)=old_r
  (s.display.shading.light,s.display.shading.color_type,s.display.shading.show_cavity)=old_sh
  bpy.data.objects.remove(camera,do_unlink=True);bpy.data.cameras.remove(data,do_unlink=True)
 assert path.is_file()
 return sha(path)
def edit():
 import bpy
 gate()
 assert Path(bpy.data.filepath).resolve()==IN.resolve()
 assert not OUTPUT.exists() and not RC.exists()
 OUT.mkdir(parents=True,exist_ok=True)
 ms=all_meshes();before={name:sig(o) for name,o in ms.items()}
 prior_counts={name:(len(o.data.vertices),len(o.data.polygons)) for name,o in ms.items()}
 render_before=render(OUT/"dashboard_detail_before.png",ms,True)
 context_before=render(OUT/"dashboard_context_before.png",ms,False)
 assert before=={name:sig(o) for name,o in ms.items()}
 initial_clearance=surface_clearance(ms[TARGET],ms)
 changed,clearance=distort(ms[TARGET],ms)
 after={name:sig(o) for name,o in ms.items()}
 assert sorted(n for n in ms if before[n]!=after[n])==[TARGET]
 assert all(prior_counts[n]==(len(o.data.vertices),len(o.data.polygons)) for n,o in ms.items())
 render_after=render(OUT/"dashboard_detail_after.png",ms,True)
 context_after=render(OUT/"dashboard_context_after.png",ms,False)
 assert after=={name:sig(o) for name,o in ms.items()} and len(bpy.data.objects)==96
 bpy.context.scene["f355spider_dashboard_first_pass"]="ORIGINAL_PMT019_CENTER_FASCIA"
 bpy.context.scene["whole_vehicle_qa_pass"]=False
 bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)
 assert sha(PMT)==PMT_SHA and sha(IN)==IN_SHA
 receipt={
  "task_id":"FERRARI16-SLOTC-F355SPIDER-DASHBOARD-NATIVE-PMT019-V1-20261110",
  "slot":"C","vehicle":"f355spider","component":"dashboard","status":"COVERED_PARTIAL_QA",
  "native_original_pmt_sha256":PMT_SHA,"original_import_blend_sha256":BASE_SHA,
  "input_blend":IN.name,"input_sha256":IN_SHA,
  "output_blend":OUTPUT.name,"output_sha256":sha(OUTPUT),
  "original_mesh":TARGET,"modified_objects":[TARGET],
  "source_mesh_fingerprints_before":before,"source_mesh_fingerprints_after":after,
  "unchanged_other_native_meshes":95,"changed_existing_vertices":len(changed),
  "changed_existing_vertex_indices":[x["vertex"] for x in changed],
  "per_vertex_geometry_deltas":changed,
  "max_displacement_m":max(x["distance_m"] for x in changed),
  "protected_windshield_original_meshes":PROTECTED,
  "closest_protected_surface_before_m":initial_clearance,
  "closest_protected_surface_after_m":clearance,
  "protected_front_glass_untouched":True,"windshield_and_other_regions_untouched":True,
  "real_photo_private":"05_F355_Spider/REF4_interior_03_f460291745.jpg",
  "real_photo_sha256":sha(PHOTO),
  "real_photo_comparison":"F355 central dashboard vents/stack qualitative position and depth; not dimensionally registered",
  "same_camera_detail_before_sha256":render_before,"same_camera_detail_after_sha256":render_after,
  "same_camera_context_before_sha256":context_before,"same_camera_context_after_sha256":context_after,
  "blender_saved":True,"independent_reopen":"PENDING",
  "full_vehicle_qa_pass":False,"next_component":"steering_wheel",
  "exports":[],"new_textures":[]
 }
 RC.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("F355_NATIVE_DASHBOARD_SAVED",receipt["output_sha256"],"modified",len(changed),"max_displacement",receipt["max_displacement_m"],"min_protected_surface",clearance,flush=True)
def reopen():
 import bpy
 gate()
 assert Path(bpy.data.filepath).resolve()==OUTPUT.resolve()
 rec=json.loads(RC.read_text())
 assert sha(OUTPUT)==rec["output_sha256"]
 ms=all_meshes()
 after={name:sig(o) for name,o in ms.items()}
 assert after==rec["source_mesh_fingerprints_after"]
 assert sorted(n for n in ms if rec["source_mesh_fingerprints_before"][n]!=after[n])==[TARGET]
 assert surface_clearance(ms[TARGET],ms)>.065
 assert bpy.context.scene["f355spider_dashboard_first_pass"]=="ORIGINAL_PMT019_CENTER_FASCIA"
 assert bpy.context.scene["whole_vehicle_qa_pass"] is False
 assert sha(PMT)==PMT_SHA and sha(BASE)==BASE_SHA and sha(IN)==IN_SHA
 rec["independent_reopen"]="PASS_BLENDER_4_5_15_SEPARATE_PROCESS"
 rec["independent_reopen_mesh_count"]=len(ms)
 RC.write_text(json.dumps(rec,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("F355_NATIVE_DASHBOARD_FRESH_REOPEN_PASS",sha(OUTPUT),flush=True)
def driver():
 gate();assert not OUTPUT.exists() and not RC.exists()
 for mode,blend in [("edit",IN),("reopen",OUTPUT)]:
  p=subprocess.run([str(B),"--background","-noaudio","-t","2",str(blend),"--python",str(Path(__file__).resolve()),"--",mode],text=True,capture_output=True,timeout=180,cwd=str(ROOT))
  print(mode,"returncode",p.returncode,"STDOUT",p.stdout[-3000:],"STDERR",p.stderr[-500:],flush=True)
  if p.returncode:raise SystemExit("BLENDER_"+mode+"_FAIL")
 print("NATIVE_DASHBOARD_COMPLETE",json.loads(RC.read_text())["output_sha256"],flush=True)
if __name__=="__main__":
 mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else sys.argv[1]
 if mode=="edit":edit()
 elif mode=="reopen":reopen()
 elif mode=="run":driver()
 else:raise SystemExit("BAD_MODE")