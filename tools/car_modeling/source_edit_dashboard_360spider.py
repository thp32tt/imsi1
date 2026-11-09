#!/usr/bin/env python3
"""360 Spider SLOT A: source-native dashboard fascia front-lip correction, no protected glass edits."""
from pathlib import Path
import bpy,sys,json,hashlib,struct,math
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[2]
D=R/'artifacts/slot_A/360spider/dashboard_20261110'
S=R/'artifacts/slot_A/360spider/instrument_cluster_20261110/Ferrari360Spider_InstrumentCluster_OriginalPMT_R03.blend'
O=D/'Ferrari360Spider_Dashboard_OriginalPMT_R04.blend'
RE=D/'receipt.json'
P=Path('/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_360sp_pmt.sz')
B=R/'artifacts/slot_A/360spider/source_bootstrap/Ferrari360Spider_OriginalPMT_EditableBaseline.blend'
N='PMT_object00_group01_material010_a0'
P_SHA='a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6'
B_SHA='b4f1d071119693172bbf786809da62dce8acb0c84e52d9779a6b1a996654ce57'
S_SHA='df7b2ce23530c4bdace9d301cde61526d5ef5ab80ab7f9811f35d4dda08de443'
# Exact indices within two disjoint source-native dashboard rear-edge islands.
# Connected front windshield-border edge starts z <= -.7712: DO NOT TOUCH.
# Rear/interior lip <= z -.60 to -.66 is distinct from glass-border seam.
# Lower-resolution upper dash front lip in game baseline sits too flat against
# authentic Ferrari 360 Spider black leather arch; passenger-side crown correction over 0.79m.
DY={1509:.022,1550:.022,1504:.033,1554:.033,1501:.018,1555:.018}
ROI={1496,1497,1498,1499,1500,*range(1501,1520)}
GLASS_NEAR=set(range(1524,1550))
PREVIOUS_COMPONENTS=['center_console','visible_seat','instrument_cluster']
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def gh(o):
 m=o.data;h=hashlib.sha256()
 h.update(struct.pack('<II',len(m.vertices),len(m.polygons)))
 for v in m.vertices:h.update(struct.pack('<3f',*v.co))
 for f in m.polygons:
  for i in f.vertices:h.update(struct.pack('<I',i))
 return h.hexdigest()
def inv():
 return {o.name:gh(o) for o in sorted(bpy.data.objects,key=lambda o:o.name) if o.type=='MESH'}
def guard():
 q=json.loads((R/'docs/automation/FERRARI16_GEOMETRY_QUEUE.json').read_text())
 w=json.loads((R/'docs/automation/FERRARI_COCKPIT_WORKPACK_A_360SPIDER.json').read_text())
 assert q['active_by_slot']['A']==w['car_id']=='360spider'
 assert q['active_by_slot']['C']=='f355spider'
 assert w['current_component']=='dashboard'
 assert w['dispatches_on_component']==0 and w['components']['dashboard']['status']=='NOT_STARTED'
 assert w['latest_accepted_editable_blend_sha256']==S_SHA
 assert w['latest_accepted_editable_blend_file']==str(S.relative_to(R))
 assert w['full_vehicle_qa_pass'] is False
 assert sha(P)==P_SHA and sha(B)==B_SHA and sha(S)==S_SHA
 man=json.loads((R/'artifacts/slot_A/360spider/source_bootstrap/native_import_manifest.json').read_text())
 assert man['source_pmt_sha256']==P_SHA and man['blend_sha256']==B_SHA
 assert len(man['original_mesh_object_ids'])==75
 return w,man
def check_geometry(m):
 assert len(m.vertices)==1920 and len(m.polygons)==1705
 assert set(DY)<=(ROI|{1550,1554,1555}) and set(DY).isdisjoint(GLASS_NEAR)
 assert all(-.01<=m.vertices[i].co.x<.85 and .79<m.vertices[i].co.y<.81 and -.67<m.vertices[i].co.z<-.59 for i in DY)
 # Preserve PMT split-edge native seam pairs exactly; both sides are dashboard only.
 groups={1509:(1509,1550),1504:(1504,1554),1501:(1501,1555)}
 expected=set(DY)
 assert expected=={i for g in groups.values() for i in g}
 for anchor,ids in groups.items():
  key=tuple(round(float(c),6) for c in m.vertices[anchor].co)
  match={v.index for v in m.vertices if tuple(round(float(c),6) for c in v.co)==key}
  assert match==set(ids),('unsafe-native-split',anchor,match)
  assert len({DY[i] for i in ids})==1
 # Other source-native objects must not duplicate the changed dashboard edge.
 for obj in bpy.data.objects:
  if obj.type=='MESH' and obj.name!=N:
   for v in obj.data.vertices:
    assert tuple(round(float(c),6) for c in v.co) not in [
      tuple(round(float(c),6) for c in m.vertices[i].co) for i in groups
    ],('cross-object-shared-geometry',obj.name,v.index)
 for p in PREVIOUS_COMPONENTS:
  rec=json.loads((R/('artifacts/slot_A/360spider/'+p+'_20261110/receipt.json')).read_text())
  assert set(DY).isdisjoint(rec.get('changed_native_indices',[]))
def edit():
 w,man=guard()
 assert not O.exists() and not RE.exists(),'Do not overwrite a finished edit'
 bpy.ops.wm.open_mainfile(filepath=str(S))
 bef=inv()
 assert set(bef)==set(man['native_mesh_fingerprints']) and len(bef)==75
 assert {k for k in bef if bef[k]!=man['native_mesh_fingerprints'][k]}=={N}
 assert all(o.matrix_world==Matrix.Identity(4) for o in bpy.data.objects if o.type=='MESH')
 m=bpy.data.objects[N].data
 check_geometry(m)
 old=[tuple(v.co) for v in m.vertices]
 for i,dy in DY.items():m.vertices[i].co.y+=dy
 m.update()
 changed=[v.index for v in m.vertices if tuple(v.co)!=old[v.index]]
 assert set(changed)==set(DY)
 aft=inv()
 assert {k for k in bef if bef[k]!=aft[k]}=={N}
 assert all(bef[k]==aft[k] for k in bef if k!=N)
 assert all(o.matrix_world==Matrix.Identity(4) for o in bpy.data.objects if o.type=='MESH')
 assert len(bpy.data.objects)==75
 bpy.data.objects[N]['native_dashboard_fascia_rework_R04']=True
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(O),compress=True)
 receipt={
 'slot':'A','car_id':'360spider','component':'dashboard','status':'COVERED_PARTIAL_QA',
 'run_key':'FERRARI16-SLOTA-360SPIDER-NATIVE-DASHBOARD-R04-20261110',
 'original_pmt_sha256':P_SHA,'original_import_blend_sha256':B_SHA,
 'input_blend':str(S.relative_to(R)),'input_sha256':S_SHA,
 'output_blend':str(O.relative_to(R)),'output_sha256':sha(O),
 'original_native_edited_object':N,'modified_native_mesh_objects':[N],
 'native_vertex_count':len(m.vertices),'changed_existing_native_indices':sorted(changed),
 'dy_meters_by_index':{str(i):dy for i,dy in DY.items()},
 'vertex_before_after':{str(i):{'before':list(old[i]),'after':list(m.vertices[i].co)} for i in DY},
 'other_native_mesh_count_unchanged':74,'all_other_native_vertices_unchanged':True,
 'windshield_glass_frame_A_pillars_border_unchanged':True,'protected_seam_range_indices_unchanged':sorted(GLASS_NEAR),
 'prior_console_seat_instrument_vertices_unchanged':True,
 'topology_changed':False,'mesh_transforms_changed':False,'new_meshes':0,
 'original_object_fingerprints_before':bef,'original_object_fingerprints_after':aft,
 'independent_blender_reopen':'PENDING','full_vehicle_qa_pass':False,
 'real_private_photo':'N100/20261104_16car_cockpit/04_360_Spider/01_interior.jpg',
 'photo_compare_note':'Photo shows a gently crowned upper dashboard/cowl and soft passenger-side curvature; absolute camera calibration pending.',
 'geometry_design':'Lift three existing passenger-side dashboard rear-edge contour positions (six native split-seam vertices) over 0.79 m, max 33 mm; no steering, binnacle, windscreen seam or new shape.'
 }
 RE.write_text(json.dumps(receipt,indent=2)+'\n')
 print('DASHBOARD_EDIT',len(changed),sha(O),'indices',sorted(changed),flush=True)
def verify():
 _,man=guard()
 assert O.is_file() and RE.is_file()
 rec=json.loads(RE.read_text())
 assert sha(O)==rec['output_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(S))
 bef=inv()
 old=[tuple(v.co) for v in bpy.data.objects[N].data.vertices]
 check_geometry(bpy.data.objects[N].data)
 bpy.ops.wm.open_mainfile(filepath=str(O))
 aft=inv();m=bpy.data.objects[N].data
 assert bef==rec['original_object_fingerprints_before']
 assert aft==rec['original_object_fingerprints_after']
 assert len(aft)==len(bef)==75
 assert {k for k in bef if bef[k]!=aft[k]}=={N}
 assert all(aft[k]==man['native_mesh_fingerprints'][k] for k in aft if k!=N)
 assert len(m.vertices)==1920 and len(m.polygons)==1705
 actual=[v.index for v in m.vertices if tuple(v.co)!=old[v.index]]
 assert set(actual)==set(DY)==set(rec['changed_existing_native_indices'])
 for i in DY:
  a=m.vertices[i].co;b=old[i]
  assert all(abs(float(a[j])-b[j] - (DY[i] if j==1 else 0))<1e-6 for j in range(3))
 assert all(o.matrix_world==Matrix.Identity(4) for o in bpy.data.objects if o.type=='MESH')
 rec['independent_blender_reopen']='PASS_BLENDER_4_5_15_NEW_PROCESS_75_ORIGINAL_MESHES_ONLY_6_DASH_VERTICES'
 RE.write_text(json.dumps(rec,indent=2)+'\n')
 print('DASHBOARD_REOPEN_PASS',rec['output_sha256'],len(actual),flush=True)
def render(which):
 src=S if which=='before' else O
 bpy.ops.wm.open_mainfile(filepath=str(src))
 sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH'
 sc.display.shading.color_type='OBJECT';sc.display.shading.light='STUDIO';sc.display.shading.show_cavity=True
 sc.render.resolution_x=1050;sc.render.resolution_y=690;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
 ob=bpy.data.objects[N];m=ob.data
 faces=[list(f.vertices) for f in m.polygons if set(f.vertices)<=ROI]
 assert len(faces)>=17
 # QA temporary object: never saved. Native PMT geometry is untouched by render.
 nm=bpy.data.meshes.new('QA_ONLY_NO_SAVE_DASH');nm.from_pydata([tuple(v.co) for v in m.vertices],[],faces);nm.update()
 qa=bpy.data.objects.new('QA_ONLY_NO_SAVE_DASH',nm);sc.collection.objects.link(qa);qa.color=(.86,.39,.20,1)
 others=[o for o in bpy.data.objects if o.type=='MESH' and o!=qa]
 cam=bpy.data.cameras.new('QA_DASHCAM');cam.type='ORTHO'
 c=bpy.data.objects.new('QA_DASHCAM',cam);sc.collection.objects.link(c);sc.camera=c
 views=[
 ('seated',(-.38,1.34,.55),(0,.81,-.76),1.75),
 ('overhead',(0,2.30,-.75),(0,.81,-.75),1.83),
 ]
 for view,loc,target,scale in views:
  c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();cam.ortho_scale=scale
  for o in others:o.hide_render=True
  sc.render.filepath=str(D/('dashboard_isolated_'+view+'_'+which+'.png'))
  bpy.ops.render.render(write_still=True)
 print('DASHBOARD_RENDER_PASS',which,flush=True)
if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 if args==['--edit']:edit()
 elif args==['--verify']:verify()
 elif len(args)==2 and args[0]=='--render' and args[1] in ('before','after'):render(args[1])
 else:raise SystemExit('Blender --python ... -- --edit|--verify|--render before|after')