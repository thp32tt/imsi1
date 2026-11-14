#!/usr/bin/env python3
"""Isolated external Ferrari F50 GLB vs verified OutRun original .blend POC.
Never writes original PMT, source .blend or external GLB. NOT a game replacement."""
import bpy, math, json, hashlib, struct
from pathlib import Path
from mathutils import Vector, Matrix
BASE=Path("/home/chatgpt-runner")
ROOT=BASE/"mod_trials/f50_glb_poc_20261115"
SRC=ROOT/"external_1995_ferrari_f50.glb"
NATIVE=BASE/"ferrari_compare_20261110/artifacts/slot_C/f50/instrument_cluster_v44/F50_OriginalPMT_InstrumentCluster_v44.blend"
OUT=ROOT/"F50_EXTERNAL_OVERLAY_FINAL_TEST.blend"
EXPECTED_GLB_SHA="6aa960b4d79f5e9400aaa804c2301f3c344461a88abc264d131b567575cae2dc"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def bbox(objects):
 pts=[o.matrix_world @ Vector(c) for o in objects if o.type=='MESH' for c in o.bound_box]
 assert pts
 mn=[min(p[i] for p in pts) for i in range(3)]
 mx=[max(p[i] for p in pts) for i in range(3)]
 return dict(min=mn,max=mx,extents=[mx[i]-mn[i] for i in range(3)],center=[(mn[i]+mx[i])/2 for i in range(3)])
def signature(objects):
 h=hashlib.sha256()
 for o in sorted(objects,key=lambda o:o.name):
  assert o.type=='MESH'
  h.update(o.name.encode('utf-8'))
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for p in o.data.polygons:
   h.update(struct.pack('<I',len(p.vertices)))
   for vi in p.vertices:h.update(struct.pack('<I',vi))
  for row in o.matrix_world:
   for f in row:h.update(struct.pack('<f',f))
 return h.hexdigest()
def metrics(objects):
 return {'meshes':len(objects),'vertices':sum(len(o.data.vertices) for o in objects),'triangles':sum(len(o.data.loop_triangles) for o in objects),'bounds':bbox(objects)}
assert SRC.is_file() and sha(SRC)==EXPECTED_GLB_SHA
assert NATIVE.is_file()
NATIVE_SHA=sha(NATIVE)
bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
native=[o for o in bpy.data.objects if o.type=='MESH']
assert len(native)==42
original_fp=signature(native)
before=metrics(native)
scene=bpy.context.scene
native_coll=bpy.data.collections.new('ORIGINAL_OUTRUN_F50_REFERENCE_UNCHANGED')
scene.collection.children.link(native_coll)
for o in native:
 for coll in list(o.users_collection):coll.objects.unlink(o)
 native_coll.objects.link(o)
native_coll.hide_render=True
prior=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(SRC))
external_objs=[o for o in bpy.data.objects if o not in prior]
external=[o for o in external_objs if o.type=='MESH']
assert len(external)==875,('GLB object count mismatch',len(external))
glb_before=metrics(external)
external_coll=bpy.data.collections.new('EXTERNAL_F50_GLTF_TEST_ONLY')
scene.collection.children.link(external_coll)
for o in external_objs:
 for coll in list(o.users_collection):coll.objects.unlink(o)
 external_coll.objects.link(o)
# Source: GLB is Z-up after Blender import. Original OutRun PMT is Y-up.
# Map external (x,y,z) -> OutRun (x,z,-y), then uniform scale to native length.
rot=Matrix.Rotation(-math.pi/2,4,'X')
native_b=before['bounds'];glb_b=glb_before['bounds']
scale=native_b['extents'][2]/glb_b['extents'][1]
translated_center=(rot @ Vector(glb_b['center'].copy()))
trans=Vector((native_b['center'][0]-scale*translated_center[0],
              native_b['min'][1]-scale*glb_b['min'][2],
              native_b['center'][2]-scale*translated_center[2]))
change=Matrix.Translation(trans) @ rot @ Matrix.Scale(scale,4)
roots=[o for o in external_objs if o.parent is None]
assert roots
yaw=Matrix.Translation(Vector((0,0,native_b['center'][2]))) @ Matrix.Rotation(math.pi,4,'Y') @ Matrix.Translation(Vector((0,0,-native_b['center'][2])))
for o in roots:
 old=o.matrix_world.copy()
 o.matrix_world=yaw @ change @ old
bpy.context.view_layer.update()
glb_after=metrics(external)
assert abs(glb_after['bounds']['extents'][2]-native_b['extents'][2])<0.001
assert abs(glb_after['bounds']['min'][1]-native_b['min'][1])<0.001
assert signature(native)==original_fp, 'original native geometry was changed'
# Render actual before/after from the same camera; native is not overwritten.
def render_camera(name, location, target, ortho):
 cam=bpy.data.cameras.new(name)
 obj=bpy.data.objects.new(name,cam)
 scene.collection.objects.link(obj)
 obj.location=Vector(location)
 forward=(Vector(target)-obj.location).normalized()
 right=forward.cross(Vector((0,1,0))).normalized()
 up=right.cross(forward).normalized()
 obj.rotation_euler=Matrix(((right.x,up.x,-forward.x),(right.y,up.y,-forward.y),(right.z,up.z,-forward.z))).to_euler()
 cam.type='ORTHO';cam.ortho_scale=ortho
 scene.camera=obj
 return obj
cam=render_camera('F50_COMPARE_CAMERA',(7.1,3.1,2.7),(0,0.43,0),6.55)
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='WORLD'
scene.display.shading.show_shadows=True
def snapshot(filename, ext_visible):
 native_coll.hide_render=ext_visible
 external_coll.hide_render=not ext_visible
 scene.render.filepath=str(ROOT/filename)
 bpy.ops.render.render(write_still=True)
 assert (ROOT/filename).is_file()
snapshot('F50_ORIGINAL_FULL_REAL.png',False)
snapshot('F50_EXTERNAL_FULL_REAL.png',True)
# The external model is kept as a separate collection with original PMT unchanged.
native_coll.hide_render=True
external_coll.hide_render=False
scene['poc_status']='EXTERNAL_F50_ALIGNED_BLENDER_PASS__NOT_INSTALLABLE_IN_OUTRUN'
scene['external_gltf_sha256']=EXPECTED_GLB_SHA
scene['original_pmt_sha256']='10daa1312b6cff0267b38b4c440c6007c68b470a225ca15f0c324876fd80aeab'
scene['original_blend_sha256']=NATIVE_SHA
scene['original_geometry_fingerprint_sha256']=original_fp
scene['source_author']='Ddiaz Design (per GLB metadata)'
scene['source_license_claim']='CC BY 4.0 (per GLB metadata; game-derived provenance unresolved)'
scene['source_url']='https://sketchfab.com/3d-models/1995-ferrari-f50-9d7ec096be3546e3967ebdb5e4a87e31'
scene['required_next_step']='PMT/OVC pipeline and game runtime QA; this is not an installable game mod'
bpy.ops.file.pack_all()
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
assert OUT.exists()
report={'status':'BLENDER_OVERLAY_POC_PASS__GAME_IMPORT_NOT_DONE','external_glb_sha256':EXPECTED_GLB_SHA,'external_file_bytes':SRC.stat().st_size,'original_blend_sha256':NATIVE_SHA,'original_pmt_sha256':scene['original_pmt_sha256'],'original_native_geometry_fingerprint':original_fp,'original_geometry_unmodified':signature(native)==original_fp,'native':before,'external_before_alignment':glb_before,'external_aligned':glb_after,'uniform_scale':scale,'native_blend_output':str(OUT),'output_blend_sha256':sha(OUT),'output_blend_bytes':OUT.stat().st_size,'renders':['F50_ORIGINAL_FULL_REAL.png','F50_EXTERNAL_FULL_REAL.png'],'source_author':'Ddiaz Design','license_claim':'CC-BY-4.0 (GLB metadata)','game_asset_origin_restrictions':'Unverified; do not redistribute asset until rights checked','pmt_writable':False,'game_runnable':False}
(ROOT/'manifest_onepass.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('F50_POC_FINAL',json.dumps(report,ensure_ascii=False),flush=True)