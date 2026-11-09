#!/usr/bin/env python3
"""F355 Spider SLOT=C visible_seat: original PMT seat bolster reshaping only.
No native object, face, vertex, transform or UV creation; isolated PMT material027.
"""
from pathlib import Path
import hashlib, json, struct, math, subprocess, sys
ROOT=Path("/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-visibleseat-20261110")
HERE=Path(__file__).resolve().parent
SOURCE=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f355sp_pmt.sz")
ORIGINAL=ROOT/"artifacts/slot_C/f355spider/source_bootstrap/F355Spider_OriginalPMT_SourceBaseline_v1.blend"
INPUT=ROOT/"artifacts/slot_C/f355spider/center_console_v1/F355Spider_OriginalPMT_CenterConsole_GateBezel_v1.blend"
OUT=ROOT/"artifacts/slot_C/f355spider/visible_seat_v1"
OUTPUT=OUT/"F355Spider_OriginalPMT_VisibleSeat_Bolster_v1.blend"
RECEIPT=OUT/"receipt.json"
BLENDER="/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender"
TARGET="PMT_F355SPIDER_object00_group01_material027_a0"
SOURCE_SHA="d9af341653ef44371e8df2efc4024af92d7ca03665acef04a4c3c65200bb7b11"
ORIGINAL_SHA="4fa9bdc314c5e30ab890adcff160377436540646588a36f1c4c1649c5df7186e"
INPUT_SHA="0c8667304fb6c527f54dd79557604e46a02270dee5a05ce37281c181db1d66f3"
PHOTO=Path("/home/chatgpt-runner/outrun2_vr_refs/20261104_16car_cockpit/05_F355_Spider/REF4_interior_01_4540a6cc94.jpg")
sys.path.insert(0,str(ROOT/"tools/car_modeling"))
from workspace_guard import preflight
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()
def gate():
 q=json.loads((ROOT/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json").read_text())
 w=json.loads((ROOT/"docs/automation/FERRARI_COCKPIT_WORKPACK_C_F355SPIDER.json").read_text())
 assert q["active_by_slot"]["C"]=="f355spider"
 assert w["car_id"]=="f355spider" and w["slot"]=="C"
 assert w["current_component"]=="visible_seat" and w["dispatches_on_component"]==0
 assert w["latest_accepted_editable_blend_sha256"]==INPUT_SHA
 assert w["original_import_blend_sha256"]==ORIGINAL_SHA
 assert preflight(q,w,"C","visible_seat").startswith("PASS C/f355spider")
 assert sha(SOURCE)==SOURCE_SHA and sha(ORIGINAL)==ORIGINAL_SHA and sha(INPUT)==INPUT_SHA
 assert PHOTO.is_file()
 return w
def sig(o):
 """Native geometry + transforms + indexed triangles + preserved PMT normals and UV."""
 h=hashlib.sha256()
 h.update(o.name.encode())
 h.update(struct.pack("<16d",*(float(t) for row in o.matrix_world for t in row)))
 m=o.data
 h.update(struct.pack("<QQ",len(m.vertices),len(m.polygons)))
 for v in m.vertices:h.update(struct.pack("<3d",*map(float,v.co)))
 for f in m.polygons:
  h.update(struct.pack("<I",len(f.vertices)))
  for vi in f.vertices:h.update(struct.pack("<I",vi))
 assert len(m.uv_layers)==1 and m.attributes.get("PMT_NATIVE_NORMAL")
 u=m.uv_layers[0]
 for x in u.data:h.update(struct.pack("<2f",*map(float,x.uv)))
 for x in m.attributes["PMT_NATIVE_NORMAL"].data:h.update(struct.pack("<3f",*map(float,x.vector)))
 return h.hexdigest()
def inventory():
 import bpy
 meshes={o.name:o for o in bpy.data.objects if o.type=="MESH"}
 assert len(meshes)==96 and TARGET in meshes
 assert all(k.startswith("PMT_F355SPIDER_") for k in meshes)
 for ob in meshes.values():
  assert not ob.modifiers and not ob.constraints and ob.parent is None
  assert all(abs(float(x))<1e-8 for x in ob.location)
  assert all(abs(float(x))<1e-8 for x in ob.rotation_euler)
  assert all(abs(float(x)-1)<1e-8 for x in ob.scale)
 target=meshes[TARGET]
 assert len(target.data.vertices)==188 and len(target.data.polygons)==300
 return meshes
def components(obj):
 m=obj.data;parent=list(range(len(m.vertices)))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 def union(a,b):
  a=find(a);b=find(b)
  if a!=b:parent[b]=a
 for p in m.polygons:
  indices=list(p.vertices)
  for i in indices[1:]:union(indices[0],i)
 groups={}
 for v in m.vertices:groups.setdefault(find(v.index),[]).append(v.index)
 assert len(groups)==2 and sorted(map(len,groups.values()))==[94,94]
 out={}
 for indices in groups.values():
  coords=[m.vertices[i].co for i in indices]
  x=sum(float(p.x) for p in coords)/len(coords)
  sign=-1 if x<0 else 1
  assert .35<abs(x)<.37
  assert abs(min(float(p.x) for p in coords))<.60
  out[sign]=indices
 assert len(out)==2
 return out
def smooth(a,b,x):
 t=max(0.0,min(1.0,(x-a)/(b-a)))
 return t*t*(3-2*t)
def distort(o):
 """Existing bolstered seat frame only. Keep cushions' central surface and cap seams."""
 groups=components(o)
 moved=[];per_side={}
 for side,indices in groups.items():
  count=0
  for i in indices:
   p=o.data.vertices[i].co
   x,y,z=map(float,p)
   outer=smooth(.472,.56,abs(x))
   inner=1-smooth(.207,.237,abs(x))
   cap_front=smooth(-.325,-.281,z)
   cap_top=1-smooth(.325,.385,z)
   cushion=math.exp(-((z+.165)/.155)**2)*cap_front
   shoulder=math.exp(-((z-.175)/.145)**2)*cap_top
   upper=smooth(.325,.365,y)
   dx=side*(.023*outer*(.75*cushion+.8*shoulder))
   dy=upper*(.014*outer*cushion +.010*inner*cushion+.005*outer*shoulder)
   if abs(dx)+abs(dy)<=.00015:continue
   before=p.copy()
   p.x+=dx;p.y+=dy
   moved.append({"vertex":i,"delta_m":(dx,dy,0.0),"displacement_m":float((p-before).length),"side":side})
   count+=1
  per_side[str(side)]=count
 assert per_side.get("-1",0)>=15 and per_side.get("1",0)>=15,per_side
 assert 40<=len(moved)<=170,len(moved)
 assert max(v["displacement_m"] for v in moved)<.028
 o.data.update()
 return moved,per_side
def render(path,meshes,kind="seat"):
 import bpy
 from mathutils import Vector
 s=bpy.context.scene
 orig_camera=s.camera
 saved={n:(o.hide_render,tuple(o.color)) for n,o in meshes.items()}
 render_settings=(s.render.engine,s.render.resolution_x,s.render.resolution_y,
  s.render.resolution_percentage,s.render.filepath,s.render.image_settings.file_format)
 shading=(s.display.shading.light,s.display.shading.color_type,s.display.shading.show_cavity)
 camdata=bpy.data.cameras.new("TEMP_SEAT_QA_CAM")
 cam=bpy.data.objects.new("TEMP_SEAT_QA_CAM",camdata)
 s.collection.objects.link(cam)
 try:
  cam.location=(1.5,1.5,-1.55)
  cam.rotation_euler=(Vector((.33,.53,.03))-cam.location).to_track_quat("-Z","Y").to_euler()
  camdata.type="ORTHO";camdata.ortho_scale=1.85;s.camera=cam
  s.render.engine="BLENDER_WORKBENCH"
  s.render.resolution_x=1200;s.render.resolution_y=780;s.render.resolution_percentage=100
  s.render.image_settings.file_format="PNG";s.render.filepath=str(path)
  s.display.shading.light="STUDIO";s.display.shading.color_type="OBJECT";s.display.shading.show_cavity=True
  for name,obj in meshes.items():
   obj.hide_render=kind=="seat" and name!=TARGET
   obj.color=(.32,.72,.83,1) if name==TARGET else (.65,.65,.65,1)
  bpy.ops.render.render(write_still=True)
 finally:
  for name,obj in meshes.items():obj.hide_render,obj.color=saved[name]
  s.camera=orig_camera
  (s.render.engine,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.filepath,s.render.image_settings.file_format)=render_settings
  (s.display.shading.light,s.display.shading.color_type,s.display.shading.show_cavity)=shading
  bpy.data.objects.remove(cam,do_unlink=True)
  bpy.data.cameras.remove(camdata,do_unlink=True)
 assert path.is_file()
 return sha(path)
def edit():
 import bpy
 gate()
 assert Path(bpy.data.filepath).resolve()==INPUT.resolve()
 assert not OUTPUT.exists() and not RECEIPT.exists()
 OUT.mkdir(parents=True,exist_ok=True)
 meshes=inventory()
 before={name:sig(o) for name,o in meshes.items()}
 original_counts={name:(len(o.data.vertices),len(o.data.polygons)) for name,o in meshes.items()}
 first=render(OUT/"seat_before.png",meshes)
 assert before=={name:sig(o) for name,o in meshes.items()}
 moved,per_side=distort(meshes[TARGET])
 after={name:sig(o) for name,o in meshes.items()}
 assert sorted(n for n in meshes if before[n]!=after[n])==[TARGET]
 assert all(original_counts[n]==(len(o.data.vertices),len(o.data.polygons)) for n,o in meshes.items())
 assert len(components(meshes[TARGET]))==2
 second=render(OUT/"seat_after.png",meshes)
 assert after=={name:sig(o) for name,o in meshes.items()}
 # Cross check no object (even camera) persisted from QA.
 assert len(bpy.data.objects)==96
 bpy.context.scene["f355spider_visible_seat_rework"]="NATIVE_PMT027_SOURCE_ONLY"
 bpy.context.scene["whole_vehicle_qa_pass"]=False
 bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)
 assert sha(SOURCE)==SOURCE_SHA and sha(INPUT)==INPUT_SHA
 receipt={
  "task_id":"FERRARI16-SLOTC-F355SPIDER-VISIBLE-SEAT-PMT027-V1-20261110",
  "slot":"C","vehicle":"f355spider","component":"visible_seat","status":"COVERED_PARTIAL_QA",
  "original_mesh":TARGET,"modified_objects":[TARGET],
  "native_original_pmt_sha256":SOURCE_SHA,
  "original_import_blend_sha256":ORIGINAL_SHA,
  "input_blend":INPUT.name,"input_sha256":INPUT_SHA,
  "output_blend":OUTPUT.name,"output_sha256":sha(OUTPUT),
  "source_mesh_fingerprints_before":before,"source_mesh_fingerprints_after":after,
  "unchanged_other_native_meshes":95,
  "changed_existing_vertices":len(moved),
  "changed_existing_vertex_indices":sorted(v["vertex"] for v in moved),
  "per_seat_existing_vertex_edits":per_side,
  "max_displacement_m":max(x["displacement_m"] for x in moved),
  "original_vertices":188,"original_triangles":300,
  "original_seat_connected_components":2,"vertices_per_seat":94,
  "nonseat_components_within_target_unchanged":True,
  "windshield_and_other_regions_untouched":True,
  "protected_front_glass_untouched":True,
  "seat_edit_zone":"Source-native paired seat cushion side bolster and lower backrest outer wings; center saddle, headrest tips and non-seat meshes unchanged",
  "photo_reference_private":"05_F355_Spider/REF4_interior_01_4540a6cc94.jpg",
  "photo_reference_sha256":sha(PHOTO),
  "photo_alignment":"SHAPE_VISUAL_ONLY_NOT_DIMENSIONALLY_REGISTERED",
  "blender_saved":True,"independent_reopen":"PENDING",
  "full_vehicle_qa_pass":False,"next_component":"instrument_cluster",
  "exports":[],"new_textures":[],
  "render_before_sha256":first,"render_after_sha256":second
 }
 RECEIPT.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
 print("SEAT_EDIT_SAVED",receipt["output_sha256"],"moved",len(moved),"per_side",per_side,"max_displacement_m",receipt["max_displacement_m"],flush=True)
def reopen():
 import bpy
 gate()
 assert Path(bpy.data.filepath).resolve()==OUTPUT.resolve()
 assert OUTPUT.is_file() and RECEIPT.is_file()
 rec=json.loads(RECEIPT.read_text())
 assert sha(OUTPUT)==rec["output_sha256"]
 meshes=inventory()
 a={n:sig(o) for n,o in meshes.items()}
 assert a==rec["source_mesh_fingerprints_after"]
 assert sorted(n for n in a if a[n]!=rec["source_mesh_fingerprints_before"][n])==[TARGET]
 assert all(len(o.data.polygons)>0 for o in meshes.values())
 assert len(components(meshes[TARGET]))==2
 assert bpy.context.scene["f355spider_visible_seat_rework"]=="NATIVE_PMT027_SOURCE_ONLY"
 assert bpy.context.scene["whole_vehicle_qa_pass"]==False
 assert sha(SOURCE)==SOURCE_SHA and sha(INPUT)==INPUT_SHA and sha(ORIGINAL)==ORIGINAL_SHA
 rec["independent_reopen"]="PASS_BLENDER_4_5_15_SEPARATE_PROCESS"
 rec["independent_reopen_mesh_count"]=len(meshes)
 RECEIPT.write_text(json.dumps(rec,indent=2,ensure_ascii=False)+"\n")
 print("SEAT_FRESH_REOPEN_PASS",sha(OUTPUT),"changed",rec["changed_existing_vertices"],flush=True)
def driver():
 gate()
 assert not OUTPUT.exists() and not RECEIPT.exists()
 for mode,blend in [("edit",INPUT),("reopen",OUTPUT)]:
  run=subprocess.run([BLENDER,"--background","-noaudio","-t","2",str(blend),"--python",str(Path(__file__).resolve()),"--",mode],text=True,capture_output=True,timeout=180,cwd=str(ROOT))
  print(mode,"exit",run.returncode,run.stdout[-4000:],run.stderr[-1500:],flush=True)
  if run.returncode:raise SystemExit("FAIL_"+mode)
 receipt=json.loads(RECEIPT.read_text())
 assert receipt["independent_reopen"].startswith("PASS")
 print("F355SPIDER_NATIVE_SEAT_COMPLETE",receipt["output_sha256"])
if __name__=="__main__":
 mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else sys.argv[1]
 if mode=="edit":edit()
 elif mode=="reopen":reopen()
 elif mode=="run":driver()
 else:raise SystemExit("bad mode")
