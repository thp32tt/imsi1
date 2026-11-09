#!/usr/bin/env python3
import bpy
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2]
i=r/"artifacts/slot_A/360spider/center_console_20261110/Ferrari360Spider_CenterConsole_SourceEdit_R01.blend"
o=r/"artifacts/slot_A/360spider/inner_door_20261110"
bpy.ops.wm.open_mainfile(filepath=str(i))
N="PMT_object00_group01_material010_a0";m=bpy.data.objects[N].data
for ob in bpy.data.objects:
 if ob.type=="MESH":ob.hide_render=ob.name!=N
cl=m.color_attributes.new(name="RENDER_ONLY",type="BYTE_COLOR",domain="CORNER")
for poly in m.polygons:
 for j in poly.loop_indices:
  v=m.vertices[m.loops[j].vertex_index].co
  c=(.95,.08,.05,1) if -.93<v.x<-.65 and .2<v.y<.8 and -.9<v.z<1.1 else (.23,.44,.57,1)
  cl.data[j].color=c
m.color_attributes.active_color=cl
sc=bpy.context.scene
cam=bpy.data.cameras.new("CAM_QA");cam.type="ORTHO";ob=bpy.data.objects.new("CAM_QA",cam);bpy.context.collection.objects.link(ob);sc.camera=ob
sc.render.engine="BLENDER_WORKBENCH";sc.display.shading.color_type="VERTEX";sc.display.shading.show_cavity=True
sc.render.resolution_x=1100;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format="PNG"
for name,loc,tgt,scale in [
 ("mat010_interior",(-.05,.70,.15),(-.86,.43,.15),2.6),
 ("mat010_exterior",(-2.0,.70,.15),(-.85,.43,.15),2.6),
 ("mat010_top",(-.7,2.3,.13),(-.7,.45,.13),2.6)]:
 ob.location=loc;ob.rotation_euler=(Vector(tgt)-ob.location).to_track_quat("-Z","Y").to_euler();cam.ortho_scale=scale
 sc.render.filepath=str(o/(name+".png"));bpy.ops.render.render(write_still=True)
 print("RENDERED",name)