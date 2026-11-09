#!/usr/bin/env python3
"""Ferrari F355 Spider SLOT=C native source PMT instrument binnacle brow geometry pass.
ONLY the isolated preexisting PMT material016 gauge housing upper lip vertices change.
No model synthesis, topology changes, transform edits, glass or dash changes.
"""
import sys,json,hashlib,math,struct,subprocess
from pathlib import Path
ROOT=Path("/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-instrument-20261110")
OUT=ROOT/"artifacts/slot_C/f355spider/instrument_cluster_v1"
INPUT=ROOT/"artifacts/slot_C/f355spider/visible_seat_v1/F355Spider_OriginalPMT_VisibleSeat_Bolster_v1.blend"
BASE=ROOT/"artifacts/slot_C/f355spider/source_bootstrap/F355Spider_OriginalPMT_SourceBaseline_v1.blend"
ORIG=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f355sp_pmt.sz")
PHOTO=Path("/home/chatgpt-runner/outrun2_vr_refs/20261104_16car_cockpit/05_F355_Spider/REF4_interior_01_4540a6cc94.jpg")
BLENDER="/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender"
OUTPUT=OUT/"F355Spider_OriginalPMT_InstrumentCluster_Visor_v1.blend"
RECEIPT=OUT/"receipt.json"
TARGET="PMT_F355SPIDER_object00_group01_material016_a0"
FACE="PMT_F355SPIDER_object00_group01_material011_a0"
SOURCE_SHA="d9af341653ef44371e8df2efc4024af92d7ca03665acef04a4c3c65200bb7b11"
BASE_SHA="4fa9bdc314c5e30ab890adcff160377436540646588a36f1c4c1649c5df7186e"
INPUT_SHA="6b179f9d275226ade32960ac49f52cec8149247dc43726f311cb79beeeb06802"
sys.path.insert(0,str(ROOT/"tools/car_modeling"))
from workspace_guard import preflight
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def guard():
 q=json.loads((ROOT/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json").read_text())
 w=json.loads((ROOT/"docs/automation/FERRARI_COCKPIT_WORKPACK_C_F355SPIDER.json").read_text())
 assert q["active_by_slot"]["C"]=="f355spider"
 assert w["slot"]=="C" and w["car_id"]=="f355spider"
 assert w["current_component"]=="instrument_cluster" and w["dispatches_on_component"]==0
 assert w["components"]["instrument_cluster"]["status"]=="NOT_STARTED"
 assert w["latest_accepted_editable_blend_sha256"]==INPUT_SHA
 assert w["original_import_blend_sha256"]==BASE_SHA
 assert preflight(q,w,"C","instrument_cluster").startswith("PASS C/f355spider")
 for p,h in [(ORIG,SOURCE_SHA),(BASE,BASE_SHA),(INPUT,INPUT_SHA)]:
  assert p.is_file() and sha(p)==h,(str(p),sha(p) if p.is_file() else None,h)
 assert PHOTO.is_file()
 return w
def geometry_signature(o):
 h=hashlib.sha256()
 h.update(o.name.encode("utf8"))
 h.update(struct.pack("<16d",*(float(t) for row in o.matrix_world for t in row)))
 m=o.data;h.update(struct.pack("<QQ",len(m.vertices),len(m.polygons)))
 for v in m.vertices:h.update(struct.pack("<3d",*map(float,v.co)))
 for f in m.polygons:
  h.update(struct.pack("<I",len(f.vertices)))
  for vi in f.vertices:h.update(struct.pack("<I",int(vi)))
 assert len(m.uv_layers)==1 and m.attributes.get("PMT_NATIVE_NORMAL")
 for uv in m.uv_layers[0].data:h.update(struct.pack("<2f",*map(float,uv.uv)))
 for n in m.attributes["PMT_NATIVE_NORMAL"].data:h.update(struct.pack("<3f",*map(float,n.vector)))
 return h.hexdigest()
def inventory():
 import bpy
 ms={o.name:o for o in bpy.data.objects if o.type=="MESH"}
 assert len(ms)==96 and TARGET in ms and FACE in ms
 assert all(k.startswith("PMT_F355SPIDER_") for k in ms)
 for o in ms.values():
  assert not o.modifiers and not o.constraints and o.parent is None
  assert max(abs(float(x)) for x in o.location)<1e-8
  assert max(abs(float(x)) for x in o.rotation_euler)<1e-8
  assert all(abs(float(x)-1)<1e-8 for x in o.scale)
 assert len(ms[TARGET].data.vertices)==222 and len(ms[TARGET].data.polygons)==124
 assert len(ms[FACE].data.vertices)==6
 return ms
def smooth(a,b,v):
 t=max(0.0,min(1.0,(v-a)/(b-a)))
 return t*t*(3-2*t)
def visor_sculpt(o):
 """Form a rounded and more projecting existing gauge-binnacle brow in original housing mesh.
 The source's 2D instrument face and neighboring dash stay exactly untouched.
 """
 modified=[]
 for v in o.data.vertices:
  x,y,z=map(float,v.co)
  # Tight spatial/part-specific selection, distinguish from 016's other vent/dash fragments.
  if not (-.515<x<-.193 and .782<y<.845 and -.600<z<-.545):continue
  # Feather into the existing lower edge to preserve base attachment and gauge face.
  crown=smooth(.785,.824,y)
  forward=smooth(-.597,-.564,z)
  fade=crown*forward
  if fade<=.06:continue
  lateral=min(1.0,abs(x+.3527)/.158)
  bow=1.0-.28*lateral
  dy=.022*fade*bow
  dz=.029*fade*(.86+.14*bow)
  dx=(-1.0 if x<-.3527 else 1.0)*.0055*fade
  v.co.x+=dx;v.co.y+=dy;v.co.z+=dz
  d=math.sqrt(dx*dx+dy*dy+dz*dz)
  modified.append({"index":v.index,"delta_m":[round(dx,7),round(dy,7),round(dz,7)],"displacement_m":d,"native_position_m":[x,y,z]})
 assert 15<=len(modified)<=90,("edited count",len(modified))
 assert max(m["displacement_m"] for m in modified)>.015
 assert max(m["displacement_m"] for m in modified)<.040
 o.data.update()
 return modified
def render(path,ms,context=False):
 import bpy
 from mathutils import Vector
 s=bpy.context.scene;old_cam=s.camera
 old={k:(o.hide_render,tuple(o.color)) for k,o in ms.items()}
 saved=(s.render.engine,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.filepath,s.render.image_settings.file_format)
 shading=(s.display.shading.light,s.display.shading.color_type,s.display.shading.show_cavity)
 data=bpy.data.cameras.new("TEMP_SOURCE_NATIVE_CLUSTER_QA_CAM")
 cam=bpy.data.objects.new("TEMP_SOURCE_NATIVE_CLUSTER_QA_CAM",data);s.collection.objects.link(cam)
 try:
  if context:
   cam.location=(-.54,1.0,.28)
   aim=(-.35,.73,-.66)
   data.ortho_scale=1.2
  else:
   cam.location=(-.353,.89,.015)
   aim=(-.353,.743,-.65)
   data.ortho_scale=.60
  cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat("-Z","Y").to_euler()
  data.type="ORTHO";s.camera=cam
  s.render.engine="BLENDER_WORKBENCH"
  s.render.resolution_x=1280;s.render.resolution_y=880;s.render.resolution_percentage=100
  s.render.image_settings.file_format="PNG";s.render.filepath=str(path)
  s.display.shading.light="STUDIO";s.display.shading.color_type="OBJECT";s.display.shading.show_cavity=True
  for name,o in ms.items():
   if context:
    o.hide_render=not name.startswith("PMT_F355SPIDER_object00_") or name.endswith(("material001_a0","material005_a0","material020_a0"))
   else:
    o.hide_render=name not in (TARGET,FACE)
   o.color=(.25,.64,.90,1) if name==TARGET else ((.95,.45,.20,1) if name==FACE else (.58,.58,.58,1))
  bpy.ops.render.render(write_still=True)
 finally:
  for k,o in ms.items():o.hide_render,o.color=old[k]
  s.camera=old_cam
  (s.render.engine,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.filepath,s.render.image_settings.file_format)=saved
  (s.display.shading.light,s.display.shading.color_type,s.display.shading.show_cavity)=shading
  bpy.data.objects.remove(cam,do_unlink=True)
  bpy.data.cameras.remove(data,do_unlink=True)
 assert path.is_file()
 return sha(path)
def edit():
 import bpy
 guard()
 assert Path(bpy.data.filepath).resolve()==INPUT.resolve()
 assert not OUTPUT.exists() and not RECEIPT.exists()
 OUT.mkdir(parents=True,exist_ok=True)
 ms=inventory()
 before={k:geometry_signature(o) for k,o in ms.items()}
 counts={k:(len(o.data.vertices),len(o.data.polygons)) for k,o in ms.items()}
 render_before=render(OUT/"cluster_before.png",ms)
 context_before=render(OUT/"driver_context_before.png",ms,True)
 assert before=={k:geometry_signature(o) for k,o in ms.items()}
 edits=visor_sculpt(ms[TARGET])
 after={k:geometry_signature(o) for k,o in ms.items()}
 assert sorted(k for k in ms if before[k]!=after[k])==[TARGET]
 assert all((len(o.data.vertices),len(o.data.polygons))==counts[k] for k,o in ms.items())
 assert before[FACE]==after[FACE]
 render_after=render(OUT/"cluster_after.png",ms)
 context_after=render(OUT/"driver_context_after.png",ms,True)
 assert after=={k:geometry_signature(o) for k,o in ms.items()}
 assert len(bpy.data.objects)==96
 bpy.context.scene["f355spider_instrument_cluster"]="NATIVE_PMT016_EXISTING_VISOR_ONLY"
 bpy.context.scene["whole_vehicle_qa_pass"]=False
 bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)
 rec={
  "task_id":"FERRARI16-SLOTC-F355SPIDER-INSTRUMENT-CLUSTER-NATIVE-PMT016-V1-20261110",
  "slot":"C","vehicle":"f355spider","component":"instrument_cluster",
  "status":"COVERED_PARTIAL_QA","native_original_pmt_sha256":SOURCE_SHA,
  "original_import_blend_sha256":BASE_SHA,"input_sha256":INPUT_SHA,
  "input_blend":INPUT.name,"output_sha256":sha(OUTPUT),"output_blend":OUTPUT.name,
  "original_mesh":TARGET,"modified_objects":[TARGET],
  "source_mesh_fingerprints_before":before,"source_mesh_fingerprints_after":after,
  "unchanged_other_native_meshes":95,
  "changed_existing_vertices":len(edits),
  "changed_existing_vertex_indices":[m["index"] for m in edits],
  "per_vertex_deltas":edits,
  "max_displacement_m":max(m["displacement_m"] for m in edits),
  "changed_vertex_selection_bounds":"x(-0.515,-0.193), y(0.782,0.845), z(-0.600,-0.545); isolated source instrument visor brow only",
  "native_pmt_fingerprint_other_regions_unchanged":True,
  "gauge_face_material011_untouched":True,
  "windshield_and_other_regions_untouched":True,
  "protected_front_glass_untouched":True,
  "photo_reference_private":"05_F355_Spider/REF4_interior_01_4540a6cc94.jpg",
  "photo_reference_sha256":sha(PHOTO),
  "photo_alignment":"VISUAL_SHAPE_REFERENCE_ONLY_NOT_CAMERA_REGISTERED",
  "render_before_sha256":render_before,"render_after_sha256":render_after,
  "context_before_sha256":context_before,"context_after_sha256":context_after,
  "blender_saved":True,"independent_reopen":"PENDING",
  "full_vehicle_qa_pass":False,"next_component":"dashboard","exports":[],"new_textures":[]
 }
 RECEIPT.write_text(json.dumps(rec,indent=2)+"\n")
 print("INSTRUMENT_CLUSTER_SAVED",rec["output_sha256"],"changed",len(edits),"max_displacement",rec["max_displacement_m"],flush=True)
def reopen():
 import bpy
 guard()
 assert Path(bpy.data.filepath).resolve()==OUTPUT.resolve()
 assert OUTPUT.is_file() and RECEIPT.is_file()
 rec=json.loads(RECEIPT.read_text())
 assert sha(OUTPUT)==rec["output_sha256"]
 ms=inventory();after={k:geometry_signature(o) for k,o in ms.items()}
 assert after==rec["source_mesh_fingerprints_after"]
 assert sorted(k for k in ms if after[k]!=rec["source_mesh_fingerprints_before"][k])==[TARGET]
 assert after[FACE]==rec["source_mesh_fingerprints_before"][FACE]
 assert bpy.context.scene["f355spider_instrument_cluster"]=="NATIVE_PMT016_EXISTING_VISOR_ONLY"
 assert bpy.context.scene["whole_vehicle_qa_pass"] is False
 assert sha(ORIG)==SOURCE_SHA and sha(BASE)==BASE_SHA and sha(INPUT)==INPUT_SHA
 rec["independent_reopen"]="PASS_BLENDER_4_5_15_SEPARATE_PROCESS"
 rec["independent_reopen_mesh_count"]=len(ms)
 RECEIPT.write_text(json.dumps(rec,indent=2)+"\n")
 print("INSTRUMENT_CLUSTER_FRESH_REOPEN_PASS",sha(OUTPUT),flush=True)
def driver():
 guard()
 assert not OUTPUT.exists() and not RECEIPT.exists()
 for mode,blend in (("edit",INPUT),("reopen",OUTPUT)):
  cmd=[BLENDER,"--background","-noaudio","-t","2",str(blend),"--python",str(Path(__file__).resolve()),"--",mode]
  p=subprocess.run(cmd,text=True,capture_output=True,cwd=str(ROOT),timeout=180)
  print(mode,"returncode",p.returncode,"STDOUT",p.stdout[-3000:],"STDERR",p.stderr[-1500:],flush=True)
  if p.returncode:raise SystemExit("BLENDER_"+mode+"_FAIL")
 r=json.loads(RECEIPT.read_text())
 assert r["independent_reopen"].startswith("PASS")
 print("F355_INSTRUMENT_CLUSTER_NATIVE_COMPLETE",r["output_sha256"],flush=True)
if __name__=="__main__":
 mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else sys.argv[1]
 if mode=="edit":edit()
 elif mode=="reopen":reopen()
 elif mode=="run":driver()
 else:raise SystemExit("unknown mode")