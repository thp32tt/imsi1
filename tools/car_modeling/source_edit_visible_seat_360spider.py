#!/usr/bin/env python3
"""Ferrari 360 Spider SLOT=A visible-seat source-native sculpt.
Only existing PMT_object00_group01_material010_a0 vertices; no new mesh, topology,
textures, transforms, glass region or game export. One material edit then advance.
Execute Blender 4.5.15 in separate invocations with --edit, --verify, --render before/after.
"""
from pathlib import Path
import sys,json,hashlib,struct,importlib.util
import bpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/"artifacts/slot_A/360spider/center_console_20261110/Ferrari360Spider_CenterConsole_SourceEdit_R01.blend"
BASE=ROOT/"artifacts/slot_A/360spider/source_bootstrap/Ferrari360Spider_OriginalPMT_EditableBaseline.blend"
MANI=ROOT/"artifacts/slot_A/360spider/source_bootstrap/native_import_manifest.json"
D=ROOT/"artifacts/slot_A/360spider/visible_seat_20261110"
OUTPUT=D/"Ferrari360Spider_VisibleSeat_OriginalPMT_R02.blend"
RECEIPT=D/"receipt.json"
SOURCE=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_360sp_pmt.sz")
NATIVE="PMT_object00_group01_material010_a0"
P_HASH="a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6"
B_HASH="b4f1d071119693172bbf786809da62dce8acb0c84e52d9779a6b1a996654ce57"
IN_HASH="5dabffb52ae4136b6b72f99c7975b629820f839afec2048e59035cb74d8ee612"
# Existing original seat topology, left-side source vertices. mirrored counterparts
# are mapped through original coordinate fingerprints, NEVER by arbitrary index offsets.
# Retain anchor edges. Z negative points toward front seat occupant in this PMT scene.
SEEDS={
 925:(0.0,+0.010,-0.038), # driver backrest inner lumbar support
 968:(0.0,+0.010,-0.038), # outer lumbar support
 931:(+0.006,0.0,-0.018), # inner lateral bolster, seam-preserved
 967:(-0.006,0.0,-0.018), # outer lateral bolster, seam-preserved
 939:(0.0,+0.030,0.0), # forward seat cushion central support
 941:(0.0,+0.030,0.0),
}
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def pmt_fingerprints():
 assert sha(SOURCE)==P_HASH,"original PMT SHA mismatch"
 assert sha(BASE)==B_HASH,"original import SHA mismatch"
 assert sha(INPUT)==IN_HASH,"accepted baseline SHA mismatch"
 mani=json.loads(MANI.read_text())
 assert mani["source_pmt_sha256"]==P_HASH and mani["blend_sha256"]==B_HASH
 assert len(mani["original_mesh_object_ids"])==75
 return mani
def hgeom(o):
 m=o.data;h=hashlib.sha256()
 h.update(struct.pack("<II",len(m.vertices),len(m.polygons)))
 for v in m.vertices:h.update(struct.pack("<3f",*v.co))
 for f in m.polygons:
  for i in f.vertices:h.update(struct.pack("<I",i))
 return h.hexdigest()
def inventory():
 return {o.name:hgeom(o) for o in sorted(bpy.data.objects,key=lambda o:o.name) if o.type=="MESH"}
def preflight():
 q=json.loads((ROOT/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json").read_text())
 w=json.loads((ROOT/"docs/automation/FERRARI_COCKPIT_WORKPACK_A_360SPIDER.json").read_text())
 assert q["active_by_slot"]["A"]==w["car_id"]=="360spider"
 assert w["current_component"]=="visible_seat" and w["dispatches_on_component"]==0
 assert w["components"]["visible_seat"]["status"]=="NOT_STARTED"
 assert w["latest_accepted_editable_blend_sha256"]==IN_HASH
 assert w["latest_accepted_editable_blend_file"]==str(INPUT.relative_to(ROOT))
 assert not w["full_vehicle_qa_pass"]
 return w
def coordkey(x):
 return tuple(round(float(c),5) for c in x)
def resolve_targets(m):
 idx_by_coord={}
 for v in m.vertices:
  key=coordkey(v.co);idx_by_coord.setdefault(key,[]).append(v.index)
 ds={}
 for seed,delta in SEEDS.items():
  v=m.vertices[seed]
  assert v.co.x<-.1 and .19<v.co.y<.91 and -.35<v.co.z<.42,("invalid seat target",seed,list(v.co))
  for key,disp in [(coordkey(v.co),delta),(coordkey((-v.co.x,v.co.y,v.co.z)),(-delta[0],delta[1],delta[2]))]:
   ids=idx_by_coord.get(key,[])
   assert ids and len(ids)<=4,("missing or ambiguous mirrored native PMT vertex",seed,key,ids)
   for i in ids:
    assert i not in ds or ds[i]==disp,(i,seed,ds[i],disp)
    ds[i]=disp
 assert 18<=len(ds)<=30,("unexpected changed vertex count",len(ds))
 assert all(abs(m.vertices[i].co.x)>.16 and abs(m.vertices[i].co.x)<.66 and -.3<m.vertices[i].co.z<.41 for i in ds)
 return ds
def edit():
 preflight()
 mani=pmt_fingerprints()
 assert not OUTPUT.exists() and not RECEIPT.exists(),"Do not overwrite original/native seat material pass"
 bpy.ops.wm.open_mainfile(filepath=str(INPUT))
 before=inventory();assert len(before)==75
 assert set(before)==set(mani["native_mesh_fingerprints"])
 assert {k for k in before if before[k]!=mani["native_mesh_fingerprints"][k]}=={NATIVE},"input not exactly prior 16-vertex center-console material"
 assert all(o.matrix_world==Matrix.Identity(4) for o in bpy.data.objects if o.type=="MESH")
 o=bpy.data.objects[NATIVE];m=o.data
 assert len(m.vertices)==1920 and len(m.polygons)==1705
 original=[tuple(v.co) for v in m.vertices]
 moves=resolve_targets(m)
 for i,(dx,dy,dz) in sorted(moves.items()):
  v=m.vertices[i];v.co=(v.co.x+dx,v.co.y+dy,v.co.z+dz)
 m.update()
 changed=[v.index for v in m.vertices if tuple(v.co)!=original[v.index]]
 assert sorted(changed)==sorted(moves),"Unexpected original vertex changes"
 # Explicitly preserve center-console original indices from its accepted first-pass edit.
 old_console=[1414,1415,1416,1417,1418,1419,1420,1421,1350,1353,1354,1355,1384,1385,1386,1389]
 assert not set(changed)&set(old_console)
 assert all(tuple(m.vertices[i].co)==original[i] for i in old_console)
 assert all(o.matrix_world==Matrix.Identity(4) for o in bpy.data.objects if o.type=="MESH")
 after=inventory()
 assert {k for k in before if before[k]!=after[k]}=={NATIVE},"non-target native mesh changed"
 o["source_geometry_unmodified"]=False
 o["native_visible_seat_source_vertex_edit_R02"]=True
 o["edited_mesh_fingerprint_sha256"]=after[NATIVE]
 bpy.context.preferences.filepaths.save_version=0
 D.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)
 s=sha(OUTPUT);assert s!=IN_HASH
 rec={"slot":"A","car":"360spider","target":"visible_seat","status":"COVERED_PARTIAL_QA",
 "input_blend":INPUT.name,"input_accepted_file":str(INPUT.relative_to(ROOT)),"input_sha256":IN_HASH,
 "output_blend":OUTPUT.name,"output_accepted_file":str(OUTPUT.relative_to(ROOT)),"output_sha256":s,
 "original_native_pmt_sha256":P_HASH,"native_original_pmt_sha256":P_HASH,"original_import_blend_sha256":B_HASH,
 "source_original_mesh":NATIVE,"original_mesh":NATIVE,"component":"visible_seat","vehicle":"360spider","modified_objects":[NATIVE],
 "source_mesh_changed":True,"native_existing_vertices_changed":len(changed),"changed_existing_vertices":len(changed),"changed_native_indices":changed,
 "changed_existing_vertex_deltas":{str(i):list(moves[i]) for i in changed},
 "source_mesh_fingerprints_before":before,"source_mesh_fingerprints_after":after,
 "preserved_other_original_meshes":74,"unchanged_other_native_meshes":74,
 "nonseat_components_within_target_unchanged":True,"windshield_and_other_regions_untouched":True,
 "previous_accepted_console_indices_unchanged":True,
 "protected_windshield_glass_frame_A_pillars_geometry_unchanged":True,
 "new_objects":0,"new_faces":0,"topology_changed":False,"blender_saved":True,
 "independent_reopen":"PENDING","full_vehicle_qa_pass":False,
 "N100_private_photo_reference":"outrun2_vr_refs/20261104_16car_cockpit/04_360_Spider/01_interior.jpg (not published)",
 "design_note":"Original paired driver/passenger seat cushion and backrest sculpt: shallow lumbar bolsters raised toward occupants up to 38 mm, inner/outer edge detail up to 18 mm and front cushion support +30 mm; original seam duplicate vertices follow identical deltas.",
 "matched_photo_calibration":"PARTIAL_ONLY_NO_CALIBRATED_GAME_CAMERA",
 "exports":[],"new_textures":[],"textures_added":[]}
 RECEIPT.write_text(json.dumps(rec,indent=2)+"\n")
 print("NATIVE_SEAT_EDIT_SAVED",json.dumps({"input_sha256":IN_HASH,"output_sha256":s,"changed_original_vertices":len(changed),"native_changed":[NATIVE],"index_list":changed}),flush=True)
def verify():
 mani=pmt_fingerprints()
 assert OUTPUT.is_file() and RECEIPT.is_file()
 rec=json.loads(RECEIPT.read_text())
 assert sha(OUTPUT)==rec["output_sha256"] and rec["output_sha256"]!=IN_HASH
 bpy.ops.wm.open_mainfile(filepath=str(INPUT))
 bef=inventory()
 original=[tuple(v.co) for v in bpy.data.objects[NATIVE].data.vertices]
 oldmoves=resolve_targets(bpy.data.objects[NATIVE].data)
 bpy.ops.wm.open_mainfile(filepath=str(OUTPUT))
 got=inventory()
 assert got==rec["source_mesh_fingerprints_after"],"Reopened geometry fingerprint does not match saved receipt"
 assert {k for k in bef if bef[k]!=got[k]}=={NATIVE},"Other original native meshes modified"
 assert all(got[k]==mani["native_mesh_fingerprints"][k] for k in got if k!=NATIVE)
 assert set(got)==set(mani["native_mesh_fingerprints"]) and len(got)==75
 m=bpy.data.objects[NATIVE].data
 changed=[v.index for v in m.vertices if tuple(v.co)!=original[v.index]]
 assert sorted(changed)==sorted(oldmoves)==sorted(rec["changed_native_indices"])
 assert len(m.vertices)==1920 and len(m.polygons)==1705
 assert all(o.matrix_world==Matrix.Identity(4) for o in bpy.data.objects if o.type=="MESH"),"object transform changed"
 # Native source attribute signature guards original normals, UV and materials through separate Blender process.
 import_path=ROOT/"tools/car_modeling/import_360spider_native_pmt.py"
 sp=importlib.util.spec_from_file_location("native_pmt_360seat",import_path)
 module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
 actual={o.name:module.actual_aux(o) for o in bpy.data.objects if o.type=="MESH"}
 assert actual==mani["native_attribute_fingerprints"],"Native UV/normal attributes changed"
 rec["verified_changed_native_indices"]=sorted(changed)
 rec["verified_native_geometry_sha256_after"]=got[NATIVE]
 rec["independent_reopen"]="PASS_BLENDER_4_5_15_NATIVE_MESH_UV_NORMAL_TOPOLOGY_75_OBJECTS"
 RECEIPT.write_text(json.dumps(rec,indent=2)+"\n")
 print("NATIVE_SEAT_FRESH_REOPEN_PASS",json.dumps({"changed":len(changed),"native":NATIVE,"others_unchanged":74}),flush=True)
def render(mode):
 assert mode in ("before","after")
 src=INPUT if mode=="before" else OUTPUT
 bpy.ops.wm.open_mainfile(filepath=str(src))
 main=bpy.data.objects[NATIVE]
 for obj in bpy.data.objects:
  if obj.type=="MESH":obj.hide_render=(obj!=main)
 cam=bpy.data.cameras.new("QA_SEAT_INSPECT_ONLY");cam.type="ORTHO"
 ob=bpy.data.objects.new("QA_SEAT_INSPECT_ONLY",cam);bpy.context.collection.objects.link(ob)
 sc=bpy.context.scene;sc.camera=ob;sc.render.engine="BLENDER_WORKBENCH";sc.display.shading.color_type="MATERIAL"
 sc.display.shading.light="STUDIO";sc.display.shading.show_cavity=True
 sc.render.resolution_x=1100;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format="PNG"
 for name,loc,tgt,scale in [
  ("seat_driver_top",(-.36,2.7,.16),(-.36,.52,.16),1.5),
  ("seat_driver_oblique",(-1.40,1.7,-.9),(-.36,.57,.13),1.55),
  ("seat_driver_cabin",(-.02,1.4,-.66),(-.36,.60,.19),1.6)
 ]:
  ob.location=loc;ob.rotation_euler=(Vector(tgt)-ob.location).to_track_quat("-Z","Y").to_euler();cam.ortho_scale=scale
  sc.render.filepath=str(D/(mode+"_"+name+".png"));bpy.ops.render.render(write_still=True)
  print("SEAT_QA_RENDER",sc.render.filepath,flush=True)
if __name__=="__main__":
 args=sys.argv[sys.argv.index("--")+1:]
 assert args and args[0] in ("--edit","--verify","--render")
 if args[0]=="--edit":edit()
 elif args[0]=="--verify":verify()
 else:render(args[1])