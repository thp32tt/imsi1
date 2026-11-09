#!/usr/bin/env python3
"""Ferrari 360 Spider SLOT=A center-console: source-vertex-only local sculpt.
Original OutRun 2006 PMT source unchanged; no new mesh, texture, game export or glass edit.
Run Blender 4.5.15 --background --python thisfile -- --edit | --verify | --render before/after.
"""
from pathlib import Path
import sys,json,hashlib,struct,importlib.util
import bpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"artifacts/slot_A/360spider/source_bootstrap/Ferrari360Spider_OriginalPMT_EditableBaseline.blend"
OUTDIR=ROOT/"artifacts/slot_A/360spider/center_console_20261110"
OUT=OUTDIR/"Ferrari360Spider_CenterConsole_SourceEdit_R01.blend"
RECEIPT=OUTDIR/"receipt.json"
MANIFEST=ROOT/"artifacts/slot_A/360spider/source_bootstrap/native_import_manifest.json"
P_SRC=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_360sp_pmt.sz")
NATIVE="PMT_object00_group01_material010_a0"
P_HASH="a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6"
B_HASH="b4f1d071119693172bbf786809da62dce8acb0c84e52d9779a6b1a996654ce57"
# Connected native surface islands identified by fixed IDs from the untouched import:
# top 1412..1421, right 1350..1355, left 1384..1389.
# Lower side anchors and trailing floor interface left unchanged.
UPLIFT={
 1414:(.068,1.15),1415:(.068,1.15),1416:(.068,1.15),1417:(.068,1.15),
 1418:(.055,1.14),1419:(.055,1.14),1420:(.025,1.10),1421:(.025,1.10),
 1350:(.025,1.10),1353:(.055,1.14),1354:(.068,1.15),1355:(.068,1.15),
 1384:(.068,1.15),1385:(.068,1.15),1386:(.055,1.14),1389:(.025,1.10),
}
assert len(UPLIFT)==16
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def provenance():
 assert sha(P_SRC)==P_HASH,"original PMT changed"
 assert sha(BASE)==B_HASH,"bootstrap source .blend changed"
 data=json.loads(MANIFEST.read_text())
 assert data["source_pmt_sha256"]==P_HASH and data["blend_sha256"]==B_HASH
 return data
def hgeom(obj):
 mesh=obj.data
 d=hashlib.sha256()
 d.update(struct.pack("<II",len(mesh.vertices),len(mesh.polygons)))
 for v in mesh.vertices:d.update(struct.pack("<3f",*v.co))
 for p in mesh.polygons:
  for i in p.vertices:d.update(struct.pack("<I",i))
 return d.hexdigest()
def inventory():
 return {o.name:hgeom(o) for o in sorted(bpy.data.objects,key=lambda o:o.name) if o.type=="MESH"}
def preflight():
 q=json.loads((ROOT/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json").read_text())
 w=json.loads((ROOT/"docs/automation/FERRARI_COCKPIT_WORKPACK_A_360SPIDER.json").read_text())
 assert q["active_by_slot"]["A"]==w["car_id"]=="360spider"
 assert w["current_component"]=="center_console" and w["dispatches_on_component"]==0
 assert w["components"]["center_console"]["status"]=="NOT_STARTED"
 assert w["latest_accepted_editable_blend_sha256"]==B_HASH
def edit():
 preflight();mani=provenance()
 assert not OUT.exists() and not RECEIPT.exists(),"duplicate center-console edit forbidden"
 bpy.ops.wm.open_mainfile(filepath=str(BASE))
 before=inventory();assert len(before)==75 and before==mani["native_mesh_fingerprints"]
 assert set(before)==set(mani["original_mesh_object_ids"])
 assert all(o.type=="MESH" for o in bpy.data.objects)
 obj=bpy.data.objects[NATIVE];m=obj.data
 assert len(m.vertices)==1920 and len(m.polygons)==1705
 assert obj.matrix_world==Matrix.Identity(4)
 vertices_before=[tuple(v.co) for v in m.vertices]
 for i,(dy,scale_x) in UPLIFT.items():
  v=m.vertices[i]
  x,y,z=v.co
  assert abs(abs(x)-.09458)<.00002,"candidate no longer original tunnel geometry"
  assert .39<y<.45 and -.33<z<.42,"out of safe tunnel region"
  # A modest geometric first pass: top ridge up 2.5–6.8 cm,
  # widen upper edge 0.9–1.4 cm each side; no faces/objects created.
  v.co=(x*scale_x,y+dy,z)
 m.update()
 changed=[v.index for v in m.vertices if tuple(v.co)!=vertices_before[v.index]]
 assert sorted(changed)==sorted(UPLIFT),"unexpected vertex delta"
 assert max(abs(m.vertices[i].co.y-vertices_before[i][1]) for i in changed)<.07
 assert max(m.vertices[i].co.y for i in changed)<.52
 assert all(-.35<m.vertices[i].co.z<.43 for i in changed)
 assert len(m.polygons)==1705 and len(m.vertices)==1920
 obj["source_geometry_unmodified"]=False
 obj["native_center_console_source_vertex_edit_R01"]=True
 after=inventory()
 assert {k for k in before if before[k]!=after[k]}=={NATIVE}
 obj["edited_mesh_fingerprint_sha256"]=after[NATIVE]
 for o in bpy.data.objects: assert o.matrix_world==Matrix.Identity(4),"object transform changed"
 OUTDIR.mkdir(parents=True,exist_ok=True)
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
 output_sha=sha(OUT)
 rec={"slot":"A","vehicle":"360spider","component":"center_console",
  "status":"COVERED_PARTIAL_QA","original_mesh":NATIVE,"modified_objects":[NATIVE],
  "native_original_pmt_sha256":P_HASH,"original_import_blend_sha256":B_HASH,
  "input_blend":BASE.name,"output_blend":OUT.name,"input_sha256":B_HASH,
  "output_sha256":output_sha,"blender_saved":True,"independent_reopen":"PENDING",
  "source_mesh_fingerprints_before":before,"source_mesh_fingerprints_after":after,
  "changed_existing_vertices":len(changed),"changed_existing_vertex_indices":sorted(changed),
  "unchanged_other_native_meshes":74,"windshield_and_other_regions_untouched":True,
  "protected_region_vertex_changes":0,"new_objects":0,"new_faces":0,
  "original_native_attribute_fingerprints":mani["native_attribute_fingerprints"],
  "full_vehicle_qa_pass":False,"exports":[],"new_textures":[],
  "photo_reference":"N100 private /outrun2_vr_refs/20261104_16car_cockpit/04_360_Spider (never published)",
  "visual_match":"PARTIAL_UNCALIBRATED","source_region_vertex_islands":[1421,1355,1389],
  "geometry_change":"raise upper central-tunnel ridge +0.025 to +0.068 m; widen upper shoulders x1.10..x1.15; anchors, topology, transforms, front glass intact"}
 RECEIPT.write_text(json.dumps(rec,indent=2)+"\n")
 print("SOURCE_EDIT_SAVED",json.dumps({"input":B_HASH,"output":output_sha,"vertices":len(changed),"native_changed":[NATIVE]}),flush=True)
def verify():
 mani=provenance()
 assert OUT.is_file() and RECEIPT.is_file()
 rec=json.loads(RECEIPT.read_text())
 assert sha(OUT)==rec["output_sha256"] and rec["input_sha256"]==B_HASH
 bpy.ops.wm.open_mainfile(filepath=str(OUT))
 got=inventory()
 assert got==rec["source_mesh_fingerprints_after"],"fresh reopen mesh fingerprint mismatch"
 assert {k for k in got if got[k]!=mani["native_mesh_fingerprints"][k]}=={NATIVE}
 assert len(got)==75 and set(got)==set(mani["native_mesh_fingerprints"])
 mod=bpy.data.objects[NATIVE]
 assert len(mod.data.vertices)==1920 and len(mod.data.polygons)==1705
 for o in bpy.data.objects:assert o.matrix_world==Matrix.Identity(4),"transform modified"
 # Validate native normals and UV remain identical after an independent Blender restart.
 imp_path=ROOT/"tools/car_modeling/import_360spider_native_pmt.py"
 spec=importlib.util.spec_from_file_location("pmt_360_native",imp_path);mod0=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod0)
 aux={o.name:mod0.actual_aux(o) for o in bpy.data.objects if o.type=="MESH"}
 assert aux==mani["native_attribute_fingerprints"],"UV/original normals changed"
 # Inspect source-baseline in separate saved file: every changed vertex is exclusively target.
 bpy.ops.wm.open_mainfile(filepath=str(BASE))
 old=bpy.data.objects[NATIVE]
 baseline=[tuple(v.co) for v in old.data.vertices]
 bpy.ops.wm.open_mainfile(filepath=str(OUT))
 new=bpy.data.objects[NATIVE]
 observed=[v.index for v in new.data.vertices if tuple(v.co)!=baseline[v.index]]
 assert sorted(observed)==sorted(UPLIFT)
 rec["independent_reopen"]="PASS_BLENDER_4_5_15_SHA_NATIVE_UV_TOPOLOGY"
 rec["verified_native_geometry_after"]=got[NATIVE]
 rec["verified_changed_vertex_indices"]=sorted(observed)
 RECEIPT.write_text(json.dumps(rec,indent=2)+"\n")
 print("CENTER_CONSOLE_REOPEN_PASS",json.dumps({"target":NATIVE,"changed_vertices":len(observed),"other_native_meshes_unchanged":74}),flush=True)
def render(kind):
 assert kind in ("before","after")
 inp=BASE if kind=="before" else OUT
 bpy.ops.wm.open_mainfile(filepath=str(inp))
 for o in bpy.data.objects:
  if o.type=="MESH":o.hide_render=(o.name!=NATIVE)
 obj=bpy.data.objects[NATIVE]
 mesh=obj.data;col=mesh.color_attributes.new(name="QA_VIS_ONLY",type="BYTE_COLOR",domain="CORNER")
 for p in mesh.polygons:
  for lid in p.loop_indices:
   idx=mesh.loops[lid].vertex_index
   col.data[lid].color=(.93,.10,.07,1) if idx in UPLIFT else (.33,.48,.62,1)
 mesh.color_attributes.active_color=col
 camera=bpy.data.cameras.new("QA_Only_Camera")
 ob=bpy.data.objects.new("QA_Only_Camera",camera);bpy.context.collection.objects.link(ob)
 sc=bpy.context.scene;sc.camera=ob;camera.type="ORTHO"
 sc.render.engine="BLENDER_WORKBENCH";sc.display.shading.color_type="VERTEX"
 sc.display.shading.light="STUDIO";sc.display.shading.show_cavity=True
 sc.render.resolution_x=1000;sc.render.resolution_y=660;sc.render.resolution_percentage=100
 sc.render.image_settings.file_format="PNG"
 views=[
  ("top",(0,3.6,-.02),(0,.38,-.02),1.8),
  ("oblique",(-1.05,1.38,-.85),(0,.41,-.01),1.65),
 ]
 for v,loc,target,scale in views:
  ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()
  camera.ortho_scale=scale
  sc.render.filepath=str(OUTDIR/f"{kind}_{v}.png")
  bpy.ops.render.render(write_still=True)
  print("QA_RENDER",sc.render.filepath,flush=True)
if __name__=="__main__":
 argv=sys.argv[sys.argv.index("--")+1:]
 assert argv and argv[0] in ("--edit","--verify","--render")
 if argv[0]=="--edit":edit()
 elif argv[0]=="--verify":verify()
 else:render(argv[1])
