#!/usr/bin/env python3
"""SLOT A R46: edit only genuine original OutRun PMT017 seat vertices.

Builds an independent source-native BLEND, NOT a drop-in replacement for the
separate accepted R45 composed cockpit. No synthetic meshes or materials.
"""
import array,hashlib,json,math,subprocess,sys
from pathlib import Path
DIR=Path("/home/chatgpt-runner/worktrees/imsi1-slotA-visible-seat-20261109/artifacts/slot_A/daytona365/R46_visible_seat")
BL=Path("/home/chatgpt-runner/.cache/f50_slotc_blender_4_5_15/blender-4.5.15-linux-x64/blender")
PMT=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_dayts_pmt.sz")
ORIG=Path("/home/chatgpt-runner/work_handoff/daytona365_rework_20261107/original_game_blender/Daytona365_ORIGINAL_GAME_COCKPIT_COMPARE.blend")
R45=Path("/home/chatgpt-runner/work_handoff/ferrari16_slotA_daytona_dashboard_steering_20261108/Daytona365_SlotA_OriginalPMT005_InnerDoor_R45.blend")
PHOTO=Path("/home/chatgpt-runner/outrun2_vr_refs/20261104_16car_cockpit/02_365_GTS4_Daytona/REF5_mecum_interior_05_464b30a6d.jpg")
DETAIL=Path("/home/chatgpt-runner/outrun2_vr_refs/20261104_16car_cockpit/02_365_GTS4_Daytona/REF5_mecum_interior_02_cb27ab7aa.jpg")
OUTPUT=DIR/"Daytona365_NATIVE_PMT017_VisibleSeat_R46.blend"
AUDIT=DIR/"native_seat_r46_geometry_qa.json"
REOPEN=DIR/"native_seat_r46_fresh_reopen_qa.json"
TARGET="object00_group01_material017_a0"
TASK_ID="FERRARI16-SLOTA-DAYTONA-NATIVE-PMT017-VISIBLE-SEAT-R46-20261109"
EXPECTED={"PMT":"f393ba5c706453a4d3f71604f25cd1631594152380856462fb0a504143ba6abe",
"ORIG":"92c82ee5c4e0631195cb314e0d8e2f56a78a6a58da3c809c46b1da0f9d2c71a3",
"R45":"224131c7adc928d5d6f0377d030d5a350c59b8664c13303a2731d6dfc6e9a722"}
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for x in iter(lambda:f.read(1048576),b""):h.update(x)
 return h.hexdigest()
def gate():
 for label,p in (("PMT",PMT),("ORIG",ORIG),("R45",R45)):
  if not p.is_file() or digest(p)!=EXPECTED[label]:raise RuntimeError("BLOCKED_INPUT_SHA_"+label)
 for p in (PHOTO,DETAIL):
  if not p.is_file() or p.stat().st_size<10000:raise RuntimeError("BLOCKED_GENUINE_PHOTO_MISSING")
 if not BL.is_file():raise RuntimeError("BLOCKED_BLENDER_NOT_INSTALLED")
def signature(o):
 m=o.data;h=hashlib.sha256()
 h.update(o.name.encode())
 for row in o.matrix_world:
  h.update((",".join(format(float(x),".12g") for x in row)+";").encode())
 h.update(str((o.hide_render,o.hide_viewport)).encode())
 h.update(str(tuple(x.name if x else None for x in m.materials)).encode())
 h.update(str(tuple((x.name,x.type) for x in o.modifiers)).encode())
 a=array.array("f",[0.0])*(len(m.vertices)*3);m.vertices.foreach_get("co",a);h.update(a.tobytes())
 a=array.array("i",[0])*len(m.loops);m.loops.foreach_get("vertex_index",a);h.update(a.tobytes())
 for uv in m.uv_layers:
  a=array.array("f",[0.0])*(len(uv.data)*2);uv.data.foreach_get("uv",a)
  h.update(uv.name.encode());h.update(a.tobytes())
 return h.hexdigest()
def protected():
 import bpy
 p={o.name:signature(o) for o in bpy.data.objects if o.type=="MESH" and o.name!=TARGET}
 if len(p)!=30:raise RuntimeError("BLOCKED_PROTECTED_MESH_COUNT_"+str(len(p)))
 return p
def smooth(a,b,x):
 t=max(0.0,min(1.0,(x-a)/(b-a)))
 return t*t*(3-2*t)
def deform():
 import bpy
 from mathutils import Vector
 gate()
 if not bpy.app.version_string.startswith("4.5.15") or Path(bpy.data.filepath).resolve()!=ORIG.resolve():
  raise RuntimeError("BLOCKED_ORIGINAL_NATIVE_BLEND_CONTEXT")
 if OUTPUT.exists() or AUDIT.exists() or REOPEN.exists():raise RuntimeError("BLOCKED_IMMUTABLE_R46_ALREADY_EXISTS")
 obj=bpy.data.objects.get(TARGET)
 if obj is None or obj.type!="MESH" or (len(obj.data.vertices),len(obj.data.polygons))!=(184,300):
  raise RuntimeError("BLOCKED_NATIVE_SEAT_MESH_NOT_EXACT_184_300")
 names=sorted(o.name for o in bpy.data.objects)
 others=protected()
 before=signature(obj)
 orig_mats=tuple(x.name if x else None for x in obj.data.materials)
 orig_uv=tuple(x.name for x in obj.data.uv_layers)
 inv=obj.matrix_world.inverted().to_3x3()
 changes=[];side_counts={"L":0,"R":0};effects={"cushion_side_bolster":0,"upper_back_side_roll":0}
 for v in obj.data.vertices:
  p=obj.matrix_world@v.co
  x,y,z=float(p.x),float(p.y),float(p.z)
  side="L" if x<0 else "R"
  lateral=abs(abs(x)-.3422)
  edge=smooth(.108,.165,lateral)
  # Native left/right seat cushion: lift original side rails where photograph
  # shows padded thigh bolsters; retain outer perimeter and central pads.
  seat_z=0.0125*edge*smooth(-.535,-.46,y)*(1.0-smooth(-.13,-.02,y))*smooth(.395,.45,z)*(1.0-smooth(.54,.565,z))
  # Upper back shoulder: pull existing original PMT side-return towards the
  # occupant, only above the cushion and clear of all cockpit/glass surfaces.
  seat_y=0.0120*edge*smooth(.75,.805,z)*(1.0-smooth(.842,.865,z))*smooth(-.735,-.670,y)
  if abs(seat_y)+abs(seat_z)<.0030:continue
  old=(x,y,z)
  v.co+=inv@Vector((0,seat_y,seat_z))
  new=obj.matrix_world@v.co
  if abs(float(new.x)-x)>1e-6:raise RuntimeError("BLOCKED_NATIVE_X_MOVED")
  changes.append({"vertex":v.index,"side":side,"xyz_before":[round(q,7) for q in old],
   "xyz_after":[round(float(new[i]),7) for i in range(3)],
   "delta_y_m":round(seat_y,7),"delta_z_m":round(seat_z,7)})
  side_counts[side]+=1
  if seat_z>.0005:effects["cushion_side_bolster"]+=1
  if seat_y>.0005:effects["upper_back_side_roll"]+=1
 obj.data.update()
 if not (14<=len(changes)<=100 and min(side_counts.values())>=6):
  raise RuntimeError("BLOCKED_SEAT_DEFORMATION_SCOPE_"+str((len(changes),side_counts)))
 maxd=max(math.hypot(t["delta_y_m"],t["delta_z_m"]) for t in changes)
 if not (.007<=maxd<=.018):raise RuntimeError("BLOCKED_DEFORMATION_TOO_SMALL_OR_LARGE_"+str(maxd))
 if (len(obj.data.vertices),len(obj.data.polygons))!=(184,300):raise RuntimeError("BLOCKED_NATIVE_TOPOLOGY_CHANGED")
 if tuple(x.name if x else None for x in obj.data.materials)!=orig_mats or tuple(x.name for x in obj.data.uv_layers)!=orig_uv:
  raise RuntimeError("BLOCKED_MATERIAL_UV_CHANGED")
 if names!=sorted(o.name for o in bpy.data.objects) or protected()!=others:
  raise RuntimeError("BLOCKED_OTHER_30_MESHES_CHANGED")
 after=signature(obj)
 if after==before:raise RuntimeError("BLOCKED_UNCHANGED_NATIVE_SEAT")
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)
 qa={"task_id":TASK_ID,"slot":"A","car_id":"daytona365","scope":"visible_seat","scope_status":"COVERED_PARTIAL_QA",
 "native_original_object":TARGET,"mesh_provenance":"DIRECT_ORIGINAL_GAME_PMT_IMPORT","native_vf":[184,300],
 "native_connected_seat_components_vertex_counts":[94,90],"left_right_changed_vertices":side_counts,
 "changed_original_vertices":len(changes),"max_displacement_m":maxd,"affected_features":effects,
 "vertex_changes":changes,"target_sig_before":before,"target_sig_after":after,
 "other_30_native_mesh_signatures_unchanged":others,"no_mesh_added_or_deleted":True,
 "no_texture_pbr_export_or_windshield_modifications":True,"original_pmt_sha256":EXPECTED["PMT"],
 "original_import_blend_sha256":EXPECTED["ORIG"],"accepted_r45_integrated_scene_sha256_untouched":EXPECTED["R45"],
 "output_native_seat_only_blend_sha256":digest(OUTPUT),
 "reference_photo_sha256":{PHOTO.name:digest(PHOTO),DETAIL.name:digest(DETAIL)},
 "source_compare_note":"Original PMT017 is exact native seat mesh. Previous R45 high-density V5/V8 seats are not proven vertex-identical; they were not edited.",
 "integration_to_accepted_r45":"NOT_PERFORMED; native seat part is separate editable Blender source asset, no full-car R45 replacement",
 "full_car_QA_PASS":False,"next_region":"instrument_cluster","QA_pending":["original_game_eye_calibration","seven_view_authentic_photo_coverage","R45_scene_integration_not_done"]}
 AUDIT.write_text(json.dumps(qa,indent=2)+"\n",encoding="utf-8")
 print("BUILD_PASS",json.dumps({"output_sha":qa["output_native_seat_only_blend_sha256"],
 "native_vertices_moved":len(changes),"by_side":side_counts,"max_delta_m":maxd,"effects":effects}),flush=True)
def verify():
 import bpy
 gate()
 if Path(bpy.data.filepath).resolve()!=OUTPUT.resolve() or not AUDIT.exists():raise RuntimeError("BLOCKED_OUTPUT_REOPEN_INPUT")
 q=json.loads(AUDIT.read_text(encoding="utf-8"))
 if digest(OUTPUT)!=q["output_native_seat_only_blend_sha256"]:raise RuntimeError("BLOCKED_OUTPUT_HASH")
 o=bpy.data.objects.get(TARGET)
 if not o or signature(o)!=q["target_sig_after"]:raise RuntimeError("BLOCKED_SEAT_REOPEN_MISMATCH")
 if (len(o.data.vertices),len(o.data.polygons))!=(184,300):raise RuntimeError("BLOCKED_NATIVE_TOPOLOGY")
 if protected()!=q["other_30_native_mesh_signatures_unchanged"]:raise RuntimeError("BLOCKED_OTHER_30_CHANGED_REOPEN")
 proof={"result":"PASS_INDEPENDENT_BLENDER_4_5_15_SAVE_REOPEN","source_native_object":TARGET,
 "output_sha256":q["output_native_seat_only_blend_sha256"],"original_vertices_modified":q["changed_original_vertices"],
 "30_other_native_meshes":"BITWISE_GEOMETRY_SIGNATURE_UNCHANGED","full_car_QA_PASS":False,
 "integration_into_R45":"NOT_PERFORMED","next":"instrument_cluster"}
 REOPEN.write_text(json.dumps(proof,indent=2)+"\n",encoding="utf-8")
 print("FRESH_REOPEN_PASS",json.dumps(proof),flush=True)
if __name__=="__main__":
 gate()
 for stage in ("build","verify"):
  arg=ORIG if stage=="build" else OUTPUT
  if "--inside-" in " ".join(sys.argv):
   if "--inside-build" in sys.argv:deform()
   else:verify()
   sys.exit(0)
  cmd=[str(BL),"--background",str(arg),"--threads","1","--python",str(Path(__file__).resolve()),"--","--inside-"+stage]
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=170)
  print((p.stdout+"\n"+p.stderr)[-7000:],flush=True)
  if p.returncode or "Traceback" in p.stderr or not (OUTPUT.exists() if stage=="build" else REOPEN.exists()):raise RuntimeError("BLENDER_"+stage+"_FAILED_"+str(p.returncode))