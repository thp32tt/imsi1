#!/usr/bin/env python3
import bpy,json,collections
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];D=R/"artifacts/slot_A/360spider/instrument_cluster_20261110"
src=R/"artifacts/slot_A/360spider/visible_seat_20261110/Ferrari360Spider_VisibleSeat_OriginalPMT_R02.blend"
bpy.ops.wm.open_mainfile(filepath=str(src))
obj=bpy.data.objects["PMT_object00_group01_material010_a0"]
data=json.loads((D/"native_islands.json").read_text())
candidates=[v for v in data if v["object"]==obj.name and -0.6<v["center"][0]<-0.1 and v["center"][1]>.60 and -1.10<v["center"][2]<-.3 and v["n"]>=6]
# Parent/islands reconstructed to allow QA isolated visualization of native faces, no saved modification.
m=obj.data;parent=list(range(len(m.vertices)))
def root(a):
 while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
 return a
def join(a,b):
 a=root(a);b=root(b)
 if a!=b:parent[b]=a
for p in m.polygons:
 for b in p.vertices[1:]:join(p.vertices[0],b)
lookup={root(v["index_min"]):v for v in candidates}
selected={i for i in range(len(m.vertices)) if root(i) in lookup}
polys=[list(f.vertices) for f in m.polygons if root(f.vertices[0]) in lookup]
print("CANDIDATES",[(v["index_min"],v["n"],v["center"],v["lo"],v["hi"]) for v in candidates], "FACES",len(polys),flush=True)
new_m=bpy.data.meshes.new("QA_NATIVE_CLUSTER_ISLAND_FACES");new_m.from_pydata([tuple(v.co) for v in m.vertices],[],polys);new_m.update()
qa=bpy.data.objects.new("QA_NATIVE_CLUSTER_ISLAND_FACES_ONLY_NO_SAVE",new_m);bpy.context.collection.objects.link(qa); qa.color=(1.0,.2,.12,1.0)
s=bpy.context.scene;s.render.engine="BLENDER_WORKBENCH";s.display.shading.color_type="OBJECT";s.display.shading.light="STUDIO";s.display.shading.show_cavity=True;s.render.resolution_x=1200;s.render.resolution_y=820;s.render.image_settings.file_format="PNG"
cam=bpy.data.cameras.new("QA_INSTRUMENT_CAM");cam.type="ORTHO"
c=bpy.data.objects.new("QA_INSTRUMENT_CAM",cam);s.collection.objects.link(c);s.camera=c
views=[("seated",(-.35,1.22,.65),(-.35,.76,-.64),1.65),("top",(-.35,2.7,-.65),(-.35,.77,-.65),1.5),("reverse",(-.35,.76,-1.6),(-.35,.75,-.65),1.65)]
others=[o for o in bpy.data.objects if o.type=="MESH" and o!=qa]
for v,loc,target,scale in views:
 c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat("-Z","Y").to_euler();cam.ortho_scale=scale
 for typ in ["original","candidate_only","cluster_area"]:
  qa.hide_render=typ=="original"
  for o in others:o.hide_render=typ=="candidate_only" or (typ=="cluster_area" and o.name not in [obj.name,"PMT_object00_group01_material006_a0"])
  if typ=="cluster_area":obj.hide_render=True
  s.render.filepath=str(D/f"instrument_{typ}_{v}.png")
  bpy.ops.render.render(write_still=True)
 print("COMPLETE",v,flush=True)
print("END_NO_BLEND_SAVED",flush=True)
