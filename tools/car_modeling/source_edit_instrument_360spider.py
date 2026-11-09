#!/usr/bin/env python3
"""Ferrari 360 Spider SLOT=A native PMT instrument binnacle hood + recess, R03.
Edits existing disjoint island native vertices ONLY in PMT_object00_group01_material010_a0.
No imported/source synthesis, topology, transforms, materials, UV, exterior, glass or other part.
Blender --edit / --verify / --render=before|after; isolated original PMT gauge-cluster ROI proof.
"""
from pathlib import Path
import bpy,sys,os,json,hashlib,struct,math
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[2]
S=R/"artifacts/slot_A/360spider/visible_seat_20261110/Ferrari360Spider_VisibleSeat_OriginalPMT_R02.blend"
D=R/"artifacts/slot_A/360spider/instrument_cluster_20261110"
O=D/"Ferrari360Spider_InstrumentCluster_OriginalPMT_R03.blend"
RE=D/"receipt.json"
N="PMT_object00_group01_material010_a0"
P=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_360sp_pmt.sz")
P_SHA="a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6"
B=R/"artifacts/slot_A/360spider/source_bootstrap/Ferrari360Spider_OriginalPMT_EditableBaseline.blend"
B_SHA="b4f1d071119693172bbf786809da62dce8acb0c84e52d9779a6b1a996654ce57"
IN_SHA="af5a9a9d9650d261b1b24f56e5ff8b5291773e033c43087e000276940fbc87a2"
# Exact native indices from 5 disjoint source-backed binnacle/face islands.
# Keyed by original float position to keep split-edge original PMT seam vertices coherent.
# Y=up, Z negative=forward. Hood arch + 13-20 mm, recessed existing panel -8..32 mm.
SEEDS={
 1586:(0,.020,-.006),1587:(0,.020,-.006),
 1584:(0,.013,-.004),1588:(0,.013,-.004),
 1585:(0,.014,-.004),1589:(0,.014,-.004),
 1620:(0,0,-.032),1622:(0,0,-.032),1624:(0,0,-.032),
 1635:(0,0,-.018),
}
CANDIDATE_ISLAND_STARTS={1565,1580,1594,1617,1628}
def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def geometry_hash(o):
 m=o.data;h=hashlib.sha256()
 h.update(struct.pack("<II",len(m.vertices),len(m.polygons)))
 for v in m.vertices:h.update(struct.pack("<3f",*v.co))
 for face in m.polygons:
  for idx in face.vertices:h.update(struct.pack("<I",idx))
 return h.hexdigest()
def inventory():
 return {o.name:geometry_hash(o) for o in sorted(bpy.data.objects,key=lambda o:o.name) if o.type=="MESH"}
def governance():
 q=json.loads((R/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json").read_text())
 w=json.loads((R/"docs/automation/FERRARI_COCKPIT_WORKPACK_A_360SPIDER.json").read_text())
 assert q["active_by_slot"]["A"]==w["car_id"]=="360spider"
 assert w["current_component"]=="instrument_cluster"
 assert w["dispatches_on_component"]==0 and w["components"]["instrument_cluster"]["status"]=="NOT_STARTED"
 assert w["latest_accepted_editable_blend_sha256"]==IN_SHA
 assert w["latest_accepted_editable_blend_file"]==str(S.relative_to(R))
 assert w["source_bootstrap"]["independent_blender_reopen"]=="PASS"
 assert w["full_vehicle_qa_pass"] is False
 assert sha(P)==P_SHA and sha(B)==B_SHA and sha(S)==IN_SHA
 mani=json.loads((R/"artifacts/slot_A/360spider/source_bootstrap/native_import_manifest.json").read_text())
 assert mani["blend_sha256"]==B_SHA and mani["source_pmt_sha256"]==P_SHA
 assert len(mani["original_mesh_object_ids"])==75
 return mani
def coord(v):return tuple(round(float(x),5) for x in v)
def candidates(m):
 data=json.loads((D/"native_islands.json").read_text())
 c=[x for x in data if x["object"]==N and x["index_min"] in CANDIDATE_ISLAND_STARTS]
 assert len(c)==5 and sum(x["n"] for x in c)==64
 allowed=set().union(*(set(x["vertex_indices"]) for x in c))
 assert len(allowed)==64 and set(SEEDS)<=allowed
 assert all(-.57<m.vertices[i].co.x<-.15 and .63<m.vertices[i].co.y<.95 and -.87<m.vertices[i].co.z<-.44 for i in allowed)
 return allowed
def moved_indices(m):
 allowed=candidates(m)
 mapping={}
 for v in m.vertices:mapping.setdefault(coord(v.co),[]).append(v.index)
 moves={}
 for idx,delta in SEEDS.items():
  matching=mapping[coord(m.vertices[idx].co)]
  assert set(matching)<=allowed,(idx,matching,"not isolated original instrument geometry")
  for i in matching:
   assert i not in moves or moves[i]==delta
   moves[i]=delta
 assert 20<=len(moves)<=32,(len(moves),sorted(moves))
 # protected original native console/seat indices are strict no-touch
 c=json.loads((R/"artifacts/slot_A/360spider/center_console_20261110/receipt.json").read_text())
 s=json.loads((R/"artifacts/slot_A/360spider/visible_seat_20261110/receipt.json").read_text())
 assert set(moves).isdisjoint(c.get("changed_native_indices",[]))
 assert set(moves).isdisjoint(s["changed_native_indices"])
 return moves
def edit():
 mani=governance()
 assert not O.exists() and not RE.exists(),"do not overwrite material edit"
 bpy.ops.wm.open_mainfile(filepath=str(S))
 before=inventory()
 assert len(before)==75 and set(before)==set(mani["native_mesh_fingerprints"])
 assert {k for k in before if before[k]!=mani["native_mesh_fingerprints"][k]}=={N}
 assert all(o.matrix_world==Matrix.Identity(4) for o in bpy.data.objects if o.type=="MESH")
 obj=bpy.data.objects[N];m=obj.data
 assert len(m.vertices)==1920 and len(m.polygons)==1705
 old=[tuple(v.co) for v in m.vertices];moves=moved_indices(m)
 for idx,delta in moves.items():
  v=m.vertices[idx];v.co=(v.co.x+delta[0],v.co.y+delta[1],v.co.z+delta[2])
 m.update()
 changed=[i for i,v in enumerate(m.vertices) if tuple(v.co)!=old[i]]
 assert set(changed)==set(moves)
 after=inventory();assert {k for k in before if before[k]!=after[k]}=={N}
 assert all(o.matrix_world==Matrix.Identity(4) for o in bpy.data.objects if o.type=="MESH")
 obj["native_instrument_cluster_original_mesh_edit_R03"]=True
 obj["edited_mesh_fingerprint_sha256"]=after[N]
 obj["source_geometry_unmodified"]=False
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(O),compress=True)
 rec={"slot":"A","vehicle":"360spider","component":"instrument_cluster","status":"COVERED_PARTIAL_QA",
  "full_vehicle_qa_pass":False,"native_original_pmt_sha256":P_SHA,"original_import_blend_sha256":B_SHA,
  "input_blend":S.name,"input_accepted_file":str(S.relative_to(R)),"input_sha256":IN_SHA,
  "output_blend":O.name,"output_accepted_file":str(O.relative_to(R)),"output_sha256":sha(O),
  "original_mesh":N,"modified_objects":[N],"changed_existing_vertices":len(changed),
  "changed_native_indices":sorted(changed),"source_mesh_fingerprints_before":before,"source_mesh_fingerprints_after":after,
  "unchanged_other_native_meshes":74,"windshield_and_other_regions_untouched":True,
  "previous_console_seat_vertices_unchanged":True,"blender_saved":True,"independent_reopen":"PENDING",
  "new_native_meshes":0,"topology_changed":False,"object_transforms_changed":False,
  "exports":[],"new_textures":[],"original_source_original_game":True,
  "island_roots":sorted(CANDIDATE_ISLAND_STARTS),
  "design_note":"Existing Ferrari 360 Spider binnacle/cluster hood: native upper brow arch up to 20 mm higher and existing central instrument face recessed up to 32 mm. No invented gauges/bezel cylinders; split seams conserved.",
  "private_photo_reference":"outrun2_vr_refs/20261104_16car_cockpit/04_360_Spider/01_interior.jpg (N100 only, not uploaded)",
  "private_photo_comparison":"broad cluster hood silhouette only; exact calibrated seated camera not available",
  "source_mesh_changed":True}
 RE.write_text(json.dumps(rec,indent=2)+"\n")
 print("SOURCE_EDIT",json.dumps({"changed_vertices":len(changed),"changed_native":[N],"input":IN_SHA,"output":rec["output_sha256"],"indices":sorted(changed)}),flush=True)
def verify():
 mani=governance()
 assert O.is_file() and RE.is_file()
 rec=json.loads(RE.read_text())
 assert sha(O)==rec["output_sha256"]
 bpy.ops.wm.open_mainfile(filepath=str(S));before=inventory();m=bpy.data.objects[N].data
 old=[tuple(v.co) for v in m.vertices];expected=moved_indices(m)
 bpy.ops.wm.open_mainfile(filepath=str(O));after=inventory()
 assert after==rec["source_mesh_fingerprints_after"]
 assert before==rec["source_mesh_fingerprints_before"]
 assert {k for k in before if before[k]!=after[k]}=={N}
 assert all(after[k]==mani["native_mesh_fingerprints"][k] for k in after if k!=N)
 m=bpy.data.objects[N].data;actual=[v.index for v in m.vertices if tuple(v.co)!=old[v.index]]
 assert sorted(actual)==sorted(expected)==rec["changed_native_indices"]
 for i,ds in expected.items():
  b=old[i];a=m.vertices[i].co
  assert all(abs(float(a[j])-b[j]-ds[j])<1.e-6 for j in range(3))
 assert len(bpy.data.objects)==75
 assert len(m.vertices)==1920 and len(m.polygons)==1705
 assert all(o.matrix_world==Matrix.Identity(4) for o in bpy.data.objects if o.type=="MESH")
 rec["independent_reopen"]="PASS_BLENDER_4_5_15_NEW_PROCESS_NATIVE_GEOMETRY_AND_75_OBJECT_SHA"
 RE.write_text(json.dumps(rec,indent=2)+"\n")
 print("FRESH_REOPEN_PASS",rec["output_sha256"],len(actual),flush=True)
def render(which):
 blend=S if which=="before" else O
 bpy.ops.wm.open_mainfile(filepath=str(blend))
 scene=bpy.context.scene;scene.render.engine="BLENDER_WORKBENCH"
 scene.display.shading.color_type="OBJECT";scene.display.shading.light="STUDIO";scene.display.shading.show_cavity=True
 scene.render.resolution_x=1200;scene.render.resolution_y=820;scene.render.image_settings.file_format="PNG"
 o=bpy.data.objects[N];allowed=candidates(o.data)
 # Temporary QA-only selection of actual triangles; no save, no model replacement.
 faces=[tuple(f.vertices) for f in o.data.polygons if set(f.vertices)<=allowed]
 assert len(faces)==59,(len(faces),"instrument island triangle proof")
 qa_mesh=bpy.data.meshes.new("QA_CLUSTERMESH_RENDER_ONLY")
 qa_mesh.from_pydata([tuple(v.co) for v in o.data.vertices],[],faces);qa_mesh.update()
 qa=bpy.data.objects.new("QA_CLUSTERMESH_RENDER_ONLY",qa_mesh);scene.collection.objects.link(qa)
 qa.color=(.82,.41,.24,1)
 for x in bpy.data.objects:
  if x.type=="MESH" and x!=qa:x.hide_render=True
 cam=bpy.data.cameras.new("QA_INSTRUMENT_CAM");cam.type="ORTHO"
 c=bpy.data.objects.new("QA_INSTRUMENT_CAM",cam);scene.collection.objects.link(c);scene.camera=c
 for view,location,target,scale in [
   ("seated",(-.35,1.22,.65),(-.35,.76,-.64),1.15),
   ("reverse",(-.35,.76,-1.6),(-.35,.75,-.65),1.15),
   ("overhead",(-.35,2.7,-.65),(-.35,.77,-.65),1.15)
 ]:
  c.location=location;c.rotation_euler=(Vector(target)-c.location).to_track_quat("-Z","Y").to_euler()
  cam.ortho_scale=scale
  scene.render.filepath=str(D/("instrument_"+view+"_"+which+".png"));bpy.ops.render.render(write_still=True)
 print("RENDER_PASS",which,flush=True)
if __name__=="__main__":
 a=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
 if a==["--edit"]:edit()
 elif a==["--verify"]:verify()
 elif len(a)==2 and a[0]=="--render" and a[1] in ("before","after"):render(a[1])
 else:raise SystemExit("blender --python script -- --edit|--verify|--render before|after")
