import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path('/home/chatgpt-runner/imsi1_slotA_steering_20261110')
d=r/'artifacts/slot_A/360spider/steering_wheel_20261110';d.mkdir(parents=True,exist_ok=True)
p=r/'artifacts/slot_A/360spider/dashboard_20261110/Ferrari360Spider_Dashboard_OriginalPMT_R04.blend'
bpy.ops.wm.open_mainfile(filepath=str(p))
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.color_type='OBJECT';sc.display.shading.show_cavity=True
sc.render.resolution_x=1050;sc.render.resolution_y=700;sc.render.image_settings.file_format='PNG'
cam=bpy.data.cameras.new('QA_CAM');cam.type='ORTHO';c=bpy.data.objects.new('QA_CAM',cam);sc.collection.objects.link(c);sc.camera=c
native=bpy.data.objects['PMT_object19_group00_material001_a0']
M=bpy.data.objects['PMT_object00_group01_material010_a0']
raw=json.loads(Path('/home/chatgpt-runner/imsi1_slotA_instrument_cluster_20261110/artifacts/slot_A/360spider/instrument_cluster_20261110/native_islands.json').read_text())
ids=set()
for root in (1628,1565,1580,1594,1617):
 x=next(x for x in raw if x['object']==M.name and x['index_min']==root)
 ids.update(x['vertex_indices'])
faces=[list(p.vertices) for p in M.data.polygons if set(p.vertices)<=ids]
new=bpy.data.meshes.new('QA_INTERNAL_ORIGINAL_FRAGMENTS');new.from_pydata([tuple(v.co) for v in M.data.vertices],[],faces);new.update()
frag=bpy.data.objects.new('QA_INTERNAL_ORIGINAL_FRAGMENTS',new);sc.collection.objects.link(frag)
for subset in ('native19','material010_fragments','both'):
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=(o!=native if subset=='native19' else o!=frag if subset=='material010_fragments' else o not in (native,frag))
 native.color=(.3,.7,.9,1);frag.color=(.94,.48,.26,1)
 for view,loc,aim in [('driver',(-.365,.86,.3),(-.365,.75,-.602)),
                     ('frontal',(-.365,.85,-1.45),(-.365,.75,-.602)),
                     ('side',(-1.5,.9,-.6),(-.365,.75,-.602))]:
  c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler()
  cam.ortho_scale=.8
  sc.render.filepath=str(d/('steering_candidate_'+subset+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
  print('CANDIDATE',subset,view,flush=True)
print('NATIVE19_OBJECT',native.name,len(native.data.vertices),len(native.data.polygons),'FRAG',len(ids),len(faces),flush=True)
print('NO_EDIT_NO_SAVE',flush=True)
