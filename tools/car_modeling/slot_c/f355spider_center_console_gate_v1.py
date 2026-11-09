#!/usr/bin/env python3
"""SLOT C F355 Spider native center-console shifter bezel source geometry edit.
Exact original PMT -> editable baseline; NO invented objects and no other source mesh edits.
"""
import sys, json, struct, math, hashlib, subprocess
from pathlib import Path
ROOT=Path("/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-centerconsole-20261110")
HERE=Path(__file__).resolve().parent
BASE=ROOT/"artifacts/slot_C/f355spider/source_bootstrap/F355Spider_OriginalPMT_SourceBaseline_v1.blend"
OUT=ROOT/"artifacts/slot_C/f355spider/center_console_v1"
OUTPUT=OUT/"F355Spider_OriginalPMT_CenterConsole_GateBezel_v1.blend"
RECEIPT=OUT/"receipt.json"
BLENDER=Path("/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender")
SOURCE=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f355sp_pmt.sz")
PMT_SHA="d9af341653ef44371e8df2efc4024af92d7ca03665acef04a4c3c65200bb7b11"
BASE_SHA="4fa9bdc314c5e30ab890adcff160377436540646588a36f1c4c1649c5df7186e"
TARGET="PMT_F355SPIDER_object00_group01_material023_a0"
CONTEXT="PMT_F355SPIDER_object00_group01_material018_a0"
sys.path.insert(0,str(ROOT/"tools/car_modeling"))
from workspace_guard import preflight,check_identity
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()
def admission():
 q=json.loads((ROOT/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json").read_text())
 w=json.loads((ROOT/"docs/automation/FERRARI_COCKPIT_WORKPACK_C_F355SPIDER.json").read_text())
 check_identity(q,w,"C",True)
 assert preflight(q,w,"C","center_console").startswith("PASS C/f355spider")
 assert w["original_import_blend_sha256"]==BASE_SHA and w["migration_input_blend_sha256"]==BASE_SHA
 assert sha(BASE)==BASE_SHA and sha(SOURCE)==PMT_SHA
 return q,w
def sig(o):
 h=hashlib.sha256()
 h.update(o.name.encode())
 h.update(struct.pack("<16d",*(float(x) for row in o.matrix_world for x in row)))
 h.update(struct.pack("<QQ",len(o.data.vertices),len(o.data.polygons)))
 for v in o.data.vertices:h.update(struct.pack("<3d",*map(float,v.co)))
 for f in o.data.polygons:
  h.update(struct.pack("<I",len(f.vertices)))
  for i in f.vertices:h.update(struct.pack("<I",i))
 return h.hexdigest()
def inventory():
 import bpy
 o={x.name:x for x in bpy.data.objects if x.type=="MESH"}
 assert len(o)==96 and TARGET in o and CONTEXT in o,len(o)
 assert all(n.startswith("PMT_F355SPIDER_") for n in o)
 assert len(o[TARGET].data.vertices)==20 and len(o[TARGET].data.polygons)==10
 assert all(len(x.modifiers)==0 for x in o.values())
 return o
def render_context(path,objs):
 import bpy
 from mathutils import Vector
 sc=bpy.context.scene
 old_camera=sc.camera
 old_state={n:(o.hide_render,tuple(o.color)) for n,o in objs.items()}
 old_render=(sc.render.engine,sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage,sc.render.filepath,sc.render.image_settings.file_format)
 cam=bpy.data.cameras.new("TEMP_CENTER_CONSOLE_QA_CAMERA")
 ob=bpy.data.objects.new("TEMP_CENTER_CONSOLE_QA_CAMERA",cam)
 bpy.context.collection.objects.link(ob)
 try:
  ob.location=(0.46,1.09,-0.12)
  look=Vector((-0.02,0.39,-0.33))
  ob.rotation_euler=(look-ob.location).to_track_quat("-Z","Y").to_euler()
  cam.type="ORTHO";cam.ortho_scale=0.42
  sc.camera=ob
  sc.render.engine="BLENDER_WORKBENCH"
  sc.display.shading.light="STUDIO"
  sc.display.shading.color_type="OBJECT"
  sc.display.shading.show_cavity=True
  sc.render.resolution_x=920
  sc.render.resolution_y=740
  sc.render.resolution_percentage=100
  sc.render.filepath=str(path)
  sc.render.image_settings.file_format="PNG"
  for n,o in objs.items():
   o.hide_render=n not in (TARGET,CONTEXT)
   o.color=(0.95,0.77,0.48,1) if n==TARGET else (0.22,0.32,0.40,1)
  bpy.ops.render.render(write_still=True)
 finally:
  for n,o in objs.items():o.hide_render,o.color=old_state[n]
  sc.camera=old_camera
  (sc.render.engine,sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage,sc.render.filepath,sc.render.image_settings.file_format)=old_render
  bpy.data.objects.remove(ob,do_unlink=True)
  bpy.data.cameras.remove(cam,do_unlink=True)
 assert path.is_file()
 return sha(path)
def edit():
 import bpy
 admission()
 assert sha(BASE)==BASE_SHA and Path(bpy.data.filepath).resolve()==BASE.resolve()
 assert not OUTPUT.exists() and not RECEIPT.exists(), "one-shot must not overwrite existing output"
 OUT.mkdir(parents=True,exist_ok=True)
 objs=inventory(); target=objs[TARGET]
 before={n:sig(o) for n,o in objs.items()}
 before_img=render_context(OUT/"gate_bezel_before.png",objs)
 assert {n:sig(o) for n,o in objs.items()}==before
 changed=[];disp=[]
 cx=-0.029025
 cz=-0.356036
 for v in target.data.vertices:
  x,y,z=map(float,v.co)
  # Photographic correction: existing native 70mm-wide gate frame underfills the
  # original 214mm-wide tunnel; expand existing perimeter, no new faces.
  # Symmetric around the original gate's local center; preserve beveled side walls.
  newx=cx+(x-cx)*1.22
  newz=cz+(z-cz)*1.15
  # Lift only the existing raised upper trim edge by 1mm to keep readable lip.
  newy=y+(0.001 if y>0.398 else 0.0)
  d=math.dist((x,y,z),(newx,newy,newz))
  assert 0.003<d<0.018,(v.index,d)
  v.co=(newx,newy,newz)
  changed.append(v.index);disp.append(d)
 assert len(changed)==20
 target.data.update()
 after={n:sig(o) for n,o in objs.items()}
 changed_objs=sorted(n for n in before if before[n]!=after[n])
 assert changed_objs==[TARGET],changed_objs
 assert len(target.data.vertices)==20 and len(target.data.polygons)==10
 assert all(len(o.data.vertices)>0 and len(o.data.polygons)>0 for o in objs.values())
 after_img=render_context(OUT/"gate_bezel_after.png",objs)
 assert {n:sig(o) for n,o in objs.items()}==after
 bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)
 assert sha(SOURCE)==PMT_SHA and sha(BASE)==BASE_SHA
 rc={
 "task_id":"FERRARI16-SLOTC-F355SPIDER-NATIVE-CENTER-CONSOLE-GATE-V1-20261110",
 "slot":"C","vehicle":"f355spider","component":"center_console","status":"COVERED_PARTIAL_QA",
 "original_mesh":TARGET,"modified_objects":[TARGET],
 "native_original_pmt_sha256":PMT_SHA,
 "original_import_blend_sha256":BASE_SHA,
 "input_blend":BASE.name,"input_sha256":BASE_SHA,
 "output_blend":OUTPUT.name,"output_sha256":sha(OUTPUT),
 "source_mesh_fingerprints_before":before,"source_mesh_fingerprints_after":after,
 "unchanged_other_native_meshes":95,
 "changed_existing_vertices":len(changed),"changed_existing_vertex_indices":changed,
 "max_displacement_m":max(disp),"original_vertices":20,"original_triangles":10,
 "geometry_change":"Existing native gated shifter bezel width +22%, length +15%, raised native upper lip +1mm; preserves original faces, UVs and materials",
 "photo_reference_private":"05_F355_Spider/REF12_transmission_2_85b8b4b7c0.jpg",
 "photo_dimensional_calibration":"PROPORTIONAL_VISUAL_ONLY_NO_VERIFIED_METROLOGY",
 "windshield_and_other_regions_untouched":True,
 "protected_front_glass_untouched":True,
 "exports":[],"new_textures":[],
 "blender_saved":True,"independent_reopen":"PENDING",
 "full_vehicle_qa_pass":False,
 "before_png_sha256":before_img,"after_png_sha256":after_img
 }
 RECEIPT.write_text(json.dumps(rc,ensure_ascii=False,indent=2)+"\n")
 print("F355SPIDER_CENTER_CONSOLE_REAL_SOURCE_EDIT",rc["output_sha256"],"changed_verts",len(changed),"max_m",max(disp))
def reopen():
 import bpy
 admission()
 assert sha(OUTPUT)==json.loads(RECEIPT.read_text())["output_sha256"]
 assert Path(bpy.data.filepath).resolve()==OUTPUT.resolve()
 rec=json.loads(RECEIPT.read_text())
 objs=inventory()
 after={n:sig(o) for n,o in objs.items()}
 assert after==rec["source_mesh_fingerprints_after"]
 assert [n for n in after if rec["source_mesh_fingerprints_before"][n]!=after[n]]==[TARGET]
 assert sha(BASE)==BASE_SHA and sha(SOURCE)==PMT_SHA
 rec["independent_reopen"]="PASS_BLENDER_4_5_15_SEPARATE_PROCESS"
 RECEIPT.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
 print("F355SPIDER_CENTER_CONSOLE_REOPEN_PASS",rec["output_sha256"])
def driver():
 admission()
 assert not OUTPUT.exists() and not RECEIPT.exists()
 for op,blend in [("edit",BASE),("reopen",OUTPUT)]:
  p=subprocess.run([str(BLENDER),"--background","-noaudio","-t","2",str(blend),"--python",str(HERE/"f355spider_center_console_gate_v1.py"),"--",op],
                 capture_output=True,text=True,timeout=180,cwd=str(ROOT))
  print(op,p.returncode,p.stdout[-6000:],p.stderr[-1500:])
  if p.returncode:raise SystemExit(op+"_FAILED")
 rc=json.loads(RECEIPT.read_text())
 assert rc["independent_reopen"].startswith("PASS") and sha(OUTPUT)==rc["output_sha256"]
 print("SOURCE_CENTER_CONSOLE_EDIT_PASS",rc["output_sha256"])
if __name__=="__main__":
 mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else sys.argv[1]
 if mode=="run":driver()
 elif mode=="edit":edit()
 elif mode=="reopen":reopen()
 else:raise SystemExit("bad mode")