import bpy, math
from mathutils import Vector
from pathlib import Path
o=Path("/home/chatgpt-runner/work_handoff/ferrari16_slotC_f50_source_audit_20261108")
for obj in bpy.data.objects:
 if obj.type=="MESH":
  obj.hide_render=("object00_group01_material023_a0" not in obj.name)
  obj.color=(0.67,0.13,0.12,1) if not obj.hide_render else (.4,.4,.4,1)
cam_data=bpy.data.cameras.new("seat_qa_temp_camera")
cam=bpy.data.objects.new("seat_qa_temp_camera",cam_data)
bpy.context.collection.objects.link(cam);bpy.context.scene.camera=cam
cam.location=(2.3,1.8,-1.9)
target=Vector((0,.55,-.08))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data.type="ORTHO";cam_data.ortho_scale=2.2
sc=bpy.context.scene;sc.render.engine="BLENDER_WORKBENCH";sc.display.shading.light="STUDIO";sc.display.shading.color_type="OBJECT"
sc.render.resolution_x=950;sc.render.resolution_y=650;sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG";sc.render.film_transparent=False
sc.render.filepath=str(o/"F50_VisibleSeat_Source023_Probe.png")
bpy.ops.render.render(write_still=True)
print("SEAT_RENDER_PROBE_DONE")