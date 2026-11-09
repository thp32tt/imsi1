import bpy,math
from pathlib import Path
from mathutils import Vector
r=Path('/home/chatgpt-runner/imsi1_slotA_steering_20261110')
d=r/'artifacts/slot_A/360spider/steering_wheel_20261110';d.mkdir(parents=True,exist_ok=True)
p=r/'artifacts/slot_A/360spider/dashboard_20261110/Ferrari360Spider_Dashboard_OriginalPMT_R04.blend'
bpy.ops.wm.open_mainfile(filepath=str(p))
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.color_type='OBJECT';scene.display.shading.light='STUDIO';scene.display.shading.show_cavity=True
scene.render.resolution_x=1000;scene.render.resolution_y=700;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
cam=bpy.data.cameras.new('WHEEL_QA_CAM');cam.type='PERSP';cam.lens=35
c=bpy.data.objects.new('WHEEL_QA_CAM',cam);scene.collection.objects.link(c);scene.camera=c
views=[('driver',(-.36,1.17,1.15),(-.35,.9,-.5)),
       ('closer',(-.36,1.10,.22),(-.35,.85,-.56)),
       ('reverse',(-.36,1.0,-1.36),(-.36,.87,-.37))]
m=[o for o in bpy.data.objects if o.type=='MESH']
for subset in ('all','source010','source006','source010_006'):
 for o in m:
  o.hide_render = not (
   subset=='all' or
   (subset=='source010' and o.name=='PMT_object00_group01_material010_a0') or
   (subset=='source006' and o.name=='PMT_object00_group01_material006_a0') or
   (subset=='source010_006' and o.name in ('PMT_object00_group01_material010_a0','PMT_object00_group01_material006_a0'))
  )
  o.color=(.43,.58,.68,1) if '010_a0' in o.name else (.67,.65,.65,1)
 for vn,loc,target in views:
  c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
  scene.render.filepath=str(d/(f'original_PMT_{subset}_{vn}.png'))
  bpy.ops.render.render(write_still=True)
  print('QA_RENDER',subset,vn,flush=True)
print('QA_ONLY_NO_SOURCE_EDIT',flush=True)
