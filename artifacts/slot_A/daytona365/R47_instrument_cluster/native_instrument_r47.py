#!/usr/bin/env python3
"""Daytona SLOT A R47: original-PMT gauge bezel depth refinement only.
Preserve all original geometry outside two connected PMT015 gauge lip strips.
No dash/wheel/texture/UV/exterior/windshield edits or invented geometry.
"""
import sys,subprocess,json,hashlib,array,math
from pathlib import Path
ROOT=Path("/home/chatgpt-runner")
REPO=ROOT/"worktrees/imsi1-slotA-instrument-20261109-1303"
DIR=REPO/"artifacts/slot_A/daytona365/R47_instrument_cluster"
DIR.mkdir(parents=True,exist_ok=True)
BL=ROOT/"work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender"
ORIG=ROOT/"work_handoff/daytona365_rework_20261107/original_game_blender/Daytona365_ORIGINAL_GAME_COCKPIT_COMPARE.blend"
PMT=ROOT/"rea-input/outrun/outrun2006/Cars/obj_plcar_dayts_pmt.sz"
ACCEPTED=ROOT/"work_handoff/ferrari16_slotA_daytona_dashboard_steering_20261108/Daytona365_SlotA_OriginalPMT005_InnerDoor_R45.blend"
PHOTO=ROOT/"outrun2_vr_refs/20261104_16car_cockpit/02_365_GTS4_Daytona/REF11_steering_instrument_closeup_5769d1ef1b.jpg"
PHOTO2=ROOT/"outrun2_vr_refs/20261104_16car_cockpit/02_365_GTS4_Daytona/REF2_dashboard_original_e91527ff82f3.jpg"
OUTPUT=DIR/"Daytona365_NATIVE_PMT015_InstrumentCluster_R47.blend"
QA=DIR/"native_instrument_r47_geometry_qa.json"
REOPEN=DIR/"native_instrument_r47_fresh_reopen_qa.json"
RECEIPT=DIR/"native_instrument_r47_receipt.json"
TARGET="object00_group01_material015_a0"
GAME_SHA="f393ba5c706453a4d3f71604f25cd1631594152380856462fb0a504143ba6abe"
ORIG_SHA="92c82ee5c4e0631195cb314e0d8e2f56a78a6a58da3c809c46b1da0f9d2c71a3"
R45_SHA="224131c7adc928d5d6f0377d030d5a350c59b8664c13303a2731d6dfc6e9a722"
TASK="FERRARI16-SLOTA-DAYTONA-NATIVE-PMT015-INSTRUMENT-R47-20261109"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for data in iter(lambda:f.read(1048576),b""):h.update(data)
 return h.hexdigest()
def gate():
 for p,s in [(PMT,GAME_SHA),(ORIG,ORIG_SHA),(ACCEPTED,R45_SHA)]:
  if not p.is_file() or sha(p)!=s:raise RuntimeError("BLOCKED_INPUT_SHA "+str(p))
 for p in [PHOTO,PHOTO2]:
  if not p.is_file() or p.stat().st_size<10000:raise RuntimeError("BLOCKED_PHOTO_MISSING")
 if not BL.is_file():raise RuntimeError("BLOCKED_BLENDER_MISSING")
def signature(o):
 m=o.data;h=hashlib.sha256()
 h.update(o.name.encode())
 for row in o.matrix_world:h.update((";".join(format(float(v),".12g") for v in row)+"|").encode())
 h.update(str((o.hide_render,o.hide_viewport)).encode())
 h.update(str(tuple(x.name if x else None for x in m.materials)).encode())
 h.update(str(tuple((x.name,x.type) for x in o.modifiers)).encode())
 a=array.array("f",[0.0])*(len(m.vertices)*3);m.vertices.foreach_get("co",a);h.update(a.tobytes())
 a=array.array("i",[0])*len(m.loops);m.loops.foreach_get("vertex_index",a);h.update(a.tobytes())
 for uv in m.uv_layers:
  a=array.array("f",[0.0])*(len(uv.data)*2);uv.data.foreach_get("uv",a)
  h.update(uv.name.encode());h.update(a.tobytes())
 return h.hexdigest()
def inv():
 import bpy
 return {"PMT_"+o.name:signature(o) for o in bpy.data.objects if o.type=="MESH" and o.name.startswith(("object00_","object22_"))}
def selected_components(obj):
 # Intrinsic native connected components, anchored by original PMT vertex IDs.
 m=obj.data;adj=[set() for v in m.vertices]
 for e in m.edges:
  a,b=e.vertices;adj[a].add(b);adj[b].add(a)
 out=[]
 for seed in (229,253):
  seen={seed}; todo=[seed]
  while todo:
   k=todo.pop()
   for j in adj[k]-seen:seen.add(j);todo.append(j)
  out.append(sorted(seen))
 if len(out[0])!=20 or len(out[1])!=20 or set(out[0])&set(out[1]):
  raise RuntimeError("BLOCKED_NOT_NATIVE_GAUGE_STRIP_20x2")
 for ids,zlo,zhi in zip(out,[.74,.84],[.81,.92]):
  pts=[obj.matrix_world@m.vertices[i].co for i in ids]
  xx=[float(p.x) for p in pts];yy=[float(p.y) for p in pts];zz=[float(p.z) for p in pts]
  if not (-.65<min(xx)<-.60 and -.085<max(xx)<-.05 and .13<min(yy)<.15 and .16<max(yy)<.18
          and zlo-0.012<min(zz)<zlo+.02 and zhi-.025<max(zz)<zhi+.015):
   raise RuntimeError("BLOCKED_GAUGE_COMPONENT_BOUNDS_"+str((min(xx),max(xx),min(yy),max(yy),min(zz),max(zz))))
 return out
def build():
 import bpy
 from mathutils import Vector
 gate()
 if bpy.app.version[:3]!=(4,5,15) or Path(bpy.data.filepath).resolve()!=ORIG.resolve():raise RuntimeError("BLOCKED_NATIVE_SOURCE_CONTEXT")
 if any(x.exists() for x in (OUTPUT,QA,REOPEN,RECEIPT)):raise RuntimeError("BLOCKED_IMMUTABLE_R47_ALREADY_EXISTS")
 obj=bpy.data.objects.get(TARGET)
 if not obj or (len(obj.data.vertices),len(obj.data.polygons))!=(619,501):
  raise RuntimeError("BLOCKED_PMT015_ID_OR_TOPOLOGY")
 strips=selected_components(obj)
 original=inv()
 if len(original)!=30:raise RuntimeError("BLOCKED_NATIVE_MESH_COUNT_"+str(len(original)))
 native_before=signature(obj)
 # Genuine photo shows gauge panel with slightly proud black instrument rims;
 # deepen only the existing PMT015 twin upper/lower bezel strips (NOT
 # PMT014 instrument face, steering, dashboard, vents, or any other geometry).
 invrot=obj.matrix_world.inverted().to_3x3()
 changes=[]
 for group,ids in enumerate(strips):
  for idx in ids:
   v=obj.data.vertices[idx];p=obj.matrix_world@v.co
   x,y,z=map(float,p)
   # Existing front bevel surface has y ~0.141; rear seam ~0.167.
   # Keep rear seam intact; advance only existing lip toward driver's eye.
   depth=0.0075*max(0.,min(1.,(.1666-y)/.0255))
   if depth<0.001:continue
   v.co+=invrot@Vector((0.,-depth,0.))
   q=obj.matrix_world@v.co
   changes.append({"vertex":idx,"strip":"lower" if group==0 else "upper",
    "before":[round(a,7) for a in (x,y,z)],"after":[round(float(q[k]),7) for k in range(3)],
    "delta_y_m":round(float(q.y)-y,7)})
 obj.data.update()
 if not (12<=len(changes)<=36):raise RuntimeError("BLOCKED_UNEXPECTED_VERTEX_COUNT_"+str(len(changes)))
 after=inv()
 diff=[k for k in original if original[k]!=after[k]]
 if diff!=["PMT_"+TARGET]:raise RuntimeError("BLOCKED_NON_TARGET_NATIVE_CHANGED_"+str(diff))
 if (len(obj.data.vertices),len(obj.data.polygons))!=(619,501):raise RuntimeError("BLOCKED_TOPOLOGY_CHANGED")
 if signature(obj)==native_before:raise RuntimeError("BLOCKED_GEOMETRY_UNCHANGED")
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)
 qa={"task_id":TASK,"scope":"instrument_cluster","slot":"A","vehicle":"daytona365",
  "status":"COVERED_PARTIAL_QA","source":"DIRECT_ORIGINAL_GAME_PMT",
  "native_original_object":TARGET,"native_vertex_count":619,"native_face_count":501,
  "connected_component_anchors":[229,253],"connected_component_sizes":[len(x) for x in strips],
  "changed_original_vertices":len(changes),"maximum_lip_depth_extension_m":.0075,
  "changed_vertex_records":changes,"other_native_object_signatures_unchanged":{k:v for k,v in original.items() if k!="PMT_"+TARGET},
  "original_native_pmt_sha256":GAME_SHA,"original_import_sha256":ORIG_SHA,
  "accepted_r45_sha256_unchanged":R45_SHA,"input_sha256":ORIG_SHA,"output_sha256":sha(OUTPUT),
  "reference_photos_sha256":{p.name:sha(p) for p in (PHOTO,PHOTO2)},
  "photo_basis":"Original 365 GTS/4 driver gauge faces and protruding black rim; no exact camera calibration.",
  "sculpt_object_limit":"Only PMT015 native upper/lower cluster bezel strips; PMT014 face and all other objects untouched.",
  "source_mesh_fingerprints_before":original,"source_mesh_fingerprints_after":after,
  "full_vehicle_qa_pass":False,"integrated_into_accepted_R45":False,"next":"dashboard",
  "qa_pending":["calibrated_original_game_eye","seven_authenticated_photo_views","standalone_geometry_not_integrated"]}
 QA.write_text(json.dumps(qa,indent=2)+"\n")
 print("BUILD_PASS",json.dumps({"changed":len(changes),"sha":sha(OUTPUT),"strips":[len(x) for x in strips]}),flush=True)
def reopen():
 import bpy
 gate()
 q=json.loads(QA.read_text())
 if Path(bpy.data.filepath).resolve()!=OUTPUT.resolve() or sha(OUTPUT)!=q["output_sha256"]:
  raise RuntimeError("BLOCKED_WRONG_REOPEN_FILE")
 if inv()!=q["source_mesh_fingerprints_after"]:raise RuntimeError("BLOCKED_NATIVE_REOPEN_FINGERPRINT")
 out={"result":"PASS_INDEPENDENT_BLENDER_4_5_15_SAVE_REOPEN",
  "target":"PMT_"+TARGET,"output_sha256":sha(OUTPUT),
  "changed_existing_vertices":q["changed_original_vertices"],"other_native_meshes_unchanged":29,
  "full_vehicle_qa_pass":False}
 REOPEN.write_text(json.dumps(out,indent=2)+"\n")
 receipt={"slot":"A","vehicle":"daytona365","component":"instrument_cluster",
  "status":"COVERED_PARTIAL_QA","full_vehicle_qa_pass":False,
  "native_original_pmt_sha256":GAME_SHA,"original_import_blend_sha256":ORIG_SHA,
  "input_sha256":ORIG_SHA,"output_sha256":q["output_sha256"],
  "input_blend":ORIG.name,"output_blend":OUTPUT.name,"blender_saved":True,
  "independent_reopen":"PASS_INDEPENDENT_BLENDER_4_5_15_SAVE_REOPEN",
  "source_mesh_fingerprints_before":q["source_mesh_fingerprints_before"],
  "source_mesh_fingerprints_after":q["source_mesh_fingerprints_after"],
  "modified_objects":["PMT_"+TARGET],"original_mesh":"PMT_"+TARGET,
  "unchanged_other_native_meshes":29,"windshield_and_other_regions_untouched":True,
  "changed_existing_vertices":q["changed_original_vertices"],
  "exports":[],"new_textures":[]}
 RECEIPT.write_text(json.dumps(receipt,indent=2)+"\n")
 print("FRESH_REOPEN_PASS",json.dumps(out),flush=True)
if __name__=="__main__":
 gate()
 if "--inside-build" in sys.argv:build();sys.exit(0)
 if "--inside-reopen" in sys.argv:reopen();sys.exit(0)
 for stage,src,out in [("build",ORIG,OUTPUT),("reopen",OUTPUT,REOPEN)]:
  cmd=[str(BL),"--background",str(src),"--threads","1","--python",str(Path(__file__).resolve()),"--","--inside-"+stage]
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=160)
  print("STAGE",stage,p.returncode,p.stdout[-2500:],p.stderr[-1500:],flush=True)
  if p.returncode or not out.exists():raise RuntimeError("BLOCKED_BLENDER_STAGE_"+stage)