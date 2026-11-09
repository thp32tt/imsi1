#!/usr/bin/env python3
import bpy,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2]
S=R/"artifacts/slot_A/360spider/visible_seat_20261110/Ferrari360Spider_VisibleSeat_OriginalPMT_R02.blend"
D=R/"artifacts/slot_A/360spider/instrument_cluster_20261110"
bpy.ops.wm.open_mainfile(filepath=str(S))
scene=bpy.context.scene
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.color_type="OBJECT"
scene.display.shading.light="STUDIO"
scene.display.shading.show_cavity=True
scene.display.shading.show_shadows=True
scene.display.shading.show_specular_highlight=True
scene.render.resolution_x=1200;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format="PNG"
cam=bpy.data.cameras.new("QA_INSTRUMENT_CAMERA"); cam.type="ORTHO"
c=bpy.data.objects.new("QA_INSTRUMENT_CAMERA",cam);scene.collection.objects.link(c);scene.camera=c
names=["all","source010","front06","dashboard_subparts"]
views=[
 ("driver",(-.45,1.20,1.05),(-.32,.82,-.65),2.05),
 ("overhead",(-.45,3.6,-.47),(-.36,.8,-.53),2.15),
 ("frontal",(-.35,.88,-1.8),(-.35,.83,-.53),2.15)
]
objects=[o for o in bpy.data.objects if o.type=="MESH"]
for typ in names:
 for o in objects:
  ok=typ=="all" or (typ=="source010" and "material010" in o.name and "object00" in o.name) or (typ=="front06" and o.name.startswith("PMT_object00_group01_material006")) or (typ=="dashboard_subparts" and o.name.startswith("PMT_object00_group01") and any(s in o.name for s in ("010_a0","011_a0","012_a0","014_a0","016_a0")))
  o.hide_render=not ok
  o.color=(.35,.65,.8,1) if "010_a0" in o.name else (.65,.65,.65,1)
 for v,loc,target,scale in views:
  c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat("-Z","Y").to_euler();cam.ortho_scale=scale
  scene.render.filepath=str(D/f"probe_{typ}_{v}.png")
  bpy.ops.render.render(write_still=True)
  print("RENDER",typ,v,flush=True)
print("DONE",flush=True)
