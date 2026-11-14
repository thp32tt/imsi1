import bpy,struct,hashlib,json
from pathlib import Path
from mathutils import Vector
root=Path('/home/chatgpt-runner/mod_trials/f50_glb_poc_20261115')
out=root/'F50_EXTERNAL_OVERLAY_FINAL_TEST.blend'
glb=root/'external_1995_ferrari_f50.glb'
base=Path('/home/chatgpt-runner/ferrari_compare_20261110/artifacts/slot_C/f50/instrument_cluster_v44/F50_OriginalPMT_InstrumentCluster_v44.blend')
original=Path('/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f50_pmt.sz')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(out))
scene=bpy.context.scene
nat=[o for o in bpy.data.collections['ORIGINAL_OUTRUN_F50_REFERENCE_UNCHANGED'].objects if o.type=='MESH']
ext=[o for o in bpy.data.collections['EXTERNAL_F50_GLTF_TEST_ONLY'].objects if o.type=='MESH']
def native_sig():
 h=hashlib.sha256()
 for o in sorted(nat,key=lambda o:o.name):
  h.update(o.name.encode())
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for p in o.data.polygons:
   h.update(struct.pack('<I',len(p.vertices)))
   for vi in p.vertices:h.update(struct.pack('<I',vi))
  for row in o.matrix_world:
   for f in row:h.update(struct.pack('<f',f))
 return h.hexdigest()
assert len(nat)==42 and len(ext)==875
assert native_sig()==scene['original_geometry_fingerprint_sha256']
assert digest(glb)==scene['external_gltf_sha256']=='6aa960b4d79f5e9400aaa804c2301f3c344461a88abc264d131b567575cae2dc'
assert digest(base)==scene['original_blend_sha256']
assert digest(original)==scene['original_pmt_sha256']=='10daa1312b6cff0267b38b4c440c6007c68b470a225ca15f0c324876fd80aeab'
for f in ['F50_ORIGINAL_FULL_REAL.png','F50_EXTERNAL_FULL_REAL.png']:
 assert (root/f).is_file() and (root/f).stat().st_size>10000
assert scene.render.resolution_x==960 and scene.render.resolution_y==540
report={'status':'PASS_BLENDER_IMPORTED_ALIGNED_REOPENED_NOT_GAME_PATCH','asset_type':'F50 external glb personal test','artifact_sha256':digest(out),'artifact_bytes':out.stat().st_size,'source_glb_sha256':digest(glb),'original_out_run_pmt_sha256':digest(original),'original_blend_sha256':digest(base),'original_native_mesh_geometry_fingerprint':native_sig(),'native_source_unchanged':True,'native_meshes':42,'native_triangles':sum(len(o.data.loop_triangles) for o in nat),'external_meshes':875,'external_triangles':sum(len(o.data.loop_triangles) for o in ext),'textures':len(bpy.data.images),'screenshots':['F50_ORIGINAL_FULL_REAL.png','F50_EXTERNAL_FULL_REAL.png'],'tested_with':'Blender 4.5.15 LTS','licensed_source_claim':'Sketchfab GLB extras CC-BY 4.0 Ddiaz Design; underlying CrewRecycled provenance not verified','external_asset_redistribution_approved':False,'game_pmt_export_tested':False,'vr_runtime_tested':False}
(root/'qa_final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('F50_INDEPENDENT_REOPEN_QA',json.dumps(report,ensure_ascii=False),flush=True)