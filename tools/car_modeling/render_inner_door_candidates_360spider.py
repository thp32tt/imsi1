#!/usr/bin/env python3
"""Read-only visual QA of exact existing PMT door-region geometry."""
import bpy,sys
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parents[2]
src=root/"artifacts/slot_A/360spider/center_console_20261110/Ferrari360Spider_CenterConsole_SourceEdit_R01.blend"
out=root/"artifacts/slot_A/360spider/inner_door_20261110"
bpy.ops.wm.open_mainfile(filepath=str(src))
for o in bpy.data.objects:
 if o.type=="MESH":o.hide_render=not o.name.startswith("PMT_object00_group01_material00") and not o.name.startswith("PMT_object00_group01_material010")
main=bpy.data.objects["PMT_object00_group01_material006_a0"]
other=bpy.data.objects["PMT_object00_group01_material010_a0"]
for o in bpy.data.objects:
 if o.type=="MESH":o.hide_render=o.name not in (main.name,other.name)
def color(o):
 m=o.data;c=m.color_attributes.new(name="QA_COLOR_DO_NOT_SAVE",type="BYTE_COLOR",domain="CORNER")
 for p in m.polygons:
  for li in p.loop_indices:
   vid=m.loops[li].vertex_index
   if o==main:
    if 2917<=vid<=2934: col=(1,.13,.10,1)
    elif 2832<=vid<=2870:col=(.09,1,.16,1)
    elif 1725<=vid<=1744:col=(1,.71,.03,1)
    elif 2608<=vid<=2625:col=(1,.13,.10,1)
    elif 1405<=vid<=1440:col=(.09,1,.16,1)
    else: col=(.23,.34,.45,1)
   else: col=(.52,.54,.63,1)
   c.data[li].color=col
 m.color_attributes.active_color=c
color(main);color(other)
sc=bpy.context.scene
cam=bpy.data.cameras.new("QA_DOOR_ONLY");cam.type="ORTHO";co=bpy.data.objects.new("QA_DOOR_ONLY",cam);bpy.context.collection.objects.link(co);sc.camera=co
sc.render.engine="BLENDER_WORKBENCH";sc.display.shading.color_type="VERTEX";sc.display.shading.light="STUDIO";sc.display.shading.show_cavity=True
sc.render.resolution_x=1150;sc.render.resolution_y=750;sc.render.resolution_percentage=100;sc.render.image_settings.file_format="PNG"
for name,loc,tgt,scale in [
 ("door_from_interior",(-.1,.71,.16),(-.93,.43,.17),2.8),
 ("door_from_exterior",(-2.6,.66,.15),(-.9,.46,.15),2.85),
 ("door_top",(-.77,3.0,.15),(-.77,.4,.15),2.9),
 ("door_rear_oblique",(-.1,1.0,1.0),(-.9,.3,.0),2.5)
]:
 co.location=loc;co.rotation_euler=(Vector(tgt)-co.location).to_track_quat("-Z","Y").to_euler();cam.ortho_scale=scale
 sc.render.filepath=str(out/(name+".png"));bpy.ops.render.render(write_still=True)
 print("RENDER",sc.render.filepath,flush=True)