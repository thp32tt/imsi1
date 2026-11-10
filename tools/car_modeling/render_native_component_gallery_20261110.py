#!/usr/bin/env python3
"""Native original game PMT exact geometry closeups against last accepted Blender meshes.
Renders only existing real source objects or original faces selected into temporary view geometry.
No Blender saves, no mesh edits, no source PMT/photo publishing.
"""
from pathlib import Path
import sys,json,subprocess,hashlib
HOME=Path('/home/chatgpt-runner')
R=HOME/'ferrari_compare_20261110'
D=R/'artifacts/real_before_after_20261110'
BLENDER=HOME/'work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender'
NATIVE=R/'artifacts/slot_A/360spider/instrument_cluster_20261110/native_islands.json'
CASES={
 'daytona365':{
  'title':'Ferrari 365 GTS/4 Daytona','version':'Accepted R45','cases':['cockpit','angle'],
  'before':HOME/'work_handoff/daytona365_rework_20261107/original_game_blender/Daytona365_ORIGINAL_GAME_COCKPIT_COMPARE.blend',
  'after':HOME/'work_handoff/ferrari16_slotA_daytona_dashboard_steering_20261108/Daytona365_SlotA_OriginalPMT005_InnerDoor_R45.blend',
  'before_sha':'92c82ee5c4e0631195cb314e0d8e2f56a78a6a58da3c809c46b1da0f9d2c71a3',
  'after_sha':'224131c7adc928d5d6f0377d030d5a350c59b8664c13303a2731d6dfc6e9a722',
  'note':'Source shows six authentic PMT cockpit meshes; R45 has 113 source-derived cabin meshes. R46/R47 unmerged.'},
 'f50':{
  'title':'Ferrari F50','version':'Accepted v44','cases':['wheel','cluster'],
  'before':HOME/'work_handoff/ferrari16_slotC_f50_source_audit_20261108/F50_OriginalPMT_CockpitSource_v1.blend',
  'after':R/'artifacts/slot_C/f50/instrument_cluster_v44/F50_OriginalPMT_InstrumentCluster_v44.blend',
  'before_sha':'d82b3d024a812126da5b38c56572cfc326fbe3d1b5c0ddf8cad4cbd855119d31',
  'after_sha':'1ff620c4ede9a265b66440105c16cd318f4e9e3761ec2754d13866f0b7d7507e',
  'note':'Native wheel and instrument panel submeshes isolated for visibility. v44 is not whole-cockpit QA PASS.'},
 '360spider':{
  'title':'Ferrari 360 Spider','version':'Accepted R04','cases':['cluster','dashboard'],
  'before':R/'artifacts/slot_A/360spider/source_bootstrap/Ferrari360Spider_OriginalPMT_EditableBaseline.blend',
  'after':R/'artifacts/slot_A/360spider/dashboard_20261110/Ferrari360Spider_Dashboard_OriginalPMT_R04.blend',
  'before_sha':'b4f1d071119693172bbf786809da62dce8acb0c84e52d9779a6b1a996654ce57',
  'after_sha':'403ec48d0e9761214f20a5c22a7df608f38b3644b135b80aa185dcb559c33ad8',
  'note':'Exact native PMT010 face islands extracted for renderer only; original and final source coordinates retained.'},
 'f355spider':{
  'title':'Ferrari F355 Spider','version':'Accepted v1 integrated','cases':['wheel','cockpit'],
  'before':R/'artifacts/slot_C/f355spider/source_bootstrap/F355Spider_OriginalPMT_SourceBaseline_v1.blend',
  'after':R/'artifacts/slot_C/f355spider/steering_wheel_v1/F355Spider_OriginalPMT_Steering_ThreeSpoke_v1.blend',
  'before_sha':'4fa9bdc314c5e30ab890adcff160377436540646588a36f1c4c1649c5df7186e',
  'after_sha':'354b2d8b67839cdabdaf838d596771750f6fb8d9919fd023a4dae2c24df52518',
  'note':'Original PMT22 wheel and four cockpit edited objects isolated; no exterior / glass geometry shown.'}}
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
def blender():
 import bpy
 from mathutils import Vector
 car,stage,region,dest=sys.argv[sys.argv.index('--')+1:]
 conf=CASES[car]
 assert Path(bpy.data.filepath).resolve()==conf[stage].resolve()
 assert sha(conf[stage])==conf[stage+'_sha']
 scene=bpy.context.scene
 objs=[o for o in bpy.data.objects if o.type=='MESH']
 names=[]
 for o in objs:o.hide_render=True
 camera_type='ORTHO'
 # Every shape is sourced from the original (or accepted) editable PMT geometry.
 if car=='daytona365':
  if stage=='before':
   names=['object00_group01_material012_a0','object00_group01_material015_a0',
    'object00_group01_material016_a0','object22_group00_material000_a0',
    'object22_group00_material001_a0','object22_group00_material002_a0']
  else:names=[o.name for o in objs]
  if region=='cockpit':
   eye=(-.35,-.92,1.055);look=(-.24,.19,.797);scale=1.48
  else:
   eye=(-.71,-.85,1.19);look=(-.14,.19,.76);scale=1.85
 elif car=='f50':
  if region=='wheel':
   names=[o.name for o in objs if o.name.startswith('PMT_F50_object21_')]
   eye=(0,0,1.0);look=(0,0,0);scale=.52
  else:
   names=['PMT_F50_object00_group01_material011_a0',
    'PMT_F50_object00_group01_material028_a0']
   eye=(-.48,1.25,.20);look=(-.32,.70,-.75);scale=1.67
 elif car=='f355spider':
  if region=='wheel':
   names=['PMT_F355SPIDER_object22_group00_material001_a0',
          'PMT_F355SPIDER_object22_group00_material000_a0']
   eye=(0,0,1);look=(0,0,0);scale=.49
  else:
   names=['PMT_F355SPIDER_object00_group01_material016_a0',
    'PMT_F355SPIDER_object00_group01_material019_a0',
    'PMT_F355SPIDER_object00_group01_material023_a0',
    'PMT_F355SPIDER_object00_group01_material027_a0']
   eye=(-.40,1.18,.60);look=(-.22,.66,-.48);scale=1.65
 elif car=='360spider':
  target='PMT_object00_group01_material010_a0'
  m=bpy.data.objects[target].data
  if region=='cluster':
   islands=json.loads(NATIVE.read_text())
   ids=set()
   for v in islands:
    if v['object']==target and v['index_min'] in (1565,1580,1594,1617,1628):
     ids.update(v['vertex_indices'])
   assert len(ids)==64,len(ids)
   faces=[tuple(f.vertices) for f in m.polygons if set(f.vertices)<=ids]
   assert len(faces)==59,len(faces)
   eye=(-.35,1.22,.65);look=(-.35,.76,-.64);scale=1.13
  else:
   roi=set([1496,1497,1498,1499,1500]+list(range(1501,1520)))
   faces=[tuple(f.vertices) for f in m.polygons if set(f.vertices)<=roi]
   assert len(faces)>=17,len(faces)
   eye=(-.38,1.34,.55);look=(0,.81,-.76);scale=1.45
  new=bpy.data.meshes.new('QA_RENDER_FROM_NATIVE_ORIGINAL_FACES_ONLY')
  new.from_pydata([tuple(v.co) for v in m.vertices],[],faces)
  new.update()
  qa=bpy.data.objects.new('QA_RENDER_FROM_NATIVE_ORIGINAL_FACES_ONLY',new)
  scene.collection.objects.link(qa)
  names=[qa.name]
 else:raise RuntimeError('unsupported')
 for name in names:
  assert name in bpy.data.objects,(car,stage,region,name)
  bpy.data.objects[name].hide_render=False
 data=bpy.data.cameras.new('QA_CAMERA_SOURCE_REAL_CROP')
 cam=bpy.data.objects.new('QA_CAMERA_SOURCE_REAL_CROP',data)
 scene.collection.objects.link(cam);scene.camera=cam
 cam.location=eye
 cam.rotation_euler=(Vector(look)-cam.location).to_track_quat('-Z','Y').to_euler()
 data.type=camera_type
 data.ortho_scale=scale
 data.clip_start=.001;data.clip_end=40
 scene.render.engine='BLENDER_WORKBENCH'
 scene.render.resolution_x=1180;scene.render.resolution_y=750
 scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG'
 scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE'
 scene.display.shading.single_color=(.78,.81,.84)
 scene.display.shading.show_cavity=True
 scene.display.shading.cavity_type='BOTH'
 scene.render.filepath=dest
 bpy.ops.render.render(write_still=True)
 assert Path(dest).stat().st_size>1000
 print('NATIVE_COMPONENT_CAPTURE_OK',json.dumps({'car':car,'stage':stage,
 'region':region,'render_sha256':sha(dest),'selected_original_meshes':names,
 'original_blend_sha256':sha(bpy.data.filepath),'blend_saved':False}),flush=True)
def layout():
 from PIL import Image,ImageDraw,ImageFont,ImageChops
 D.mkdir(parents=True,exist_ok=True)
 bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',34)
 med=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
 sm=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
 foot=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
 manifest={'schema_version':2,'render':'actual Blender 4.5.15 Workbench source-derived meshes only',
  'notes':'Components isolated using only native existing geometry; no invented objects saved, no model edits.',
  'full_vehicle_qa_pass':False,'cars':{}}
 previews=[]
 for car,c in CASES.items():
  manifest['cars'][car]={'before_source_sha256':c['before_sha'],
   'after_source_sha256':c['after_sha'],'notes':c['note'],'regions':{}}
  for reg in c['cases']:
   b=Image.open(D/(car+'_'+reg+'_native_before.png')).convert('RGB')
   a=Image.open(D/(car+'_'+reg+'_native_after.png')).convert('RGB')
   assert b.size==a.size
   w,h=b.size
   canvas=Image.new('RGB',(w*2+48,h+160),(19,23,29))
   d=ImageDraw.Draw(canvas)
   d.text((26,12),c['title']+'   |   '+reg.upper()+' SOURCE MESH',font=bold,fill='#F6F8FA')
   d.text((24,64),'ORIGINAL GAME PMT',font=med,fill='#B8D1E7')
   d.text((w+45,64),'LAST ACCEPTED: '+c['version'],font=med,fill='#C8E5BE')
   canvas.paste(b,(16,98));canvas.paste(a,(w+34,98))
   d.text((23,h+104),'Real native triangle render • same camera/scale • source objects isolated, no synthetic geometry',font=sm,fill='#BFC7D0')
   d.text((23,h+131),'Not actual game camera or vehicle QA PASS. '+c['note'][:100],font=foot,fill='#ADB5BC')
   dest=D/(car+'_REAL_ORIGINAL_VS_FINAL_'+reg+'.png')
   canvas.save(dest,optimize=True)
   manifest['cars'][car]['regions'][reg]={'original_render_sha256':sha(D/(car+'_'+reg+'_native_before.png')),
     'final_render_sha256':sha(D/(car+'_'+reg+'_native_after.png')),
     'comparison_sha256':sha(dest),'difference_bbox':ImageChops.difference(b,a).getbbox()}
   if reg==c['cases'][0]:previews.append(dest)
 overview=Image.new('RGB',(2450,1105),(14,18,24))
 d=ImageDraw.Draw(overview)
 d.text((32,12),'FOUR FERRARIS | ACTUAL ORIGINAL vs FINAL MESH',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',38),fill='#F5F8FA')
 d.text((35,65),'Authentic Blender renders, not AI-generated approximations • Component isolation for visibility',font=sm,fill='#B6C0CA')
 for i,p in enumerate(previews):
  im=Image.open(p).convert('RGB')
  im.thumbnail((1190,595),Image.Resampling.LANCZOS)
  overview.paste(im,(20+(i%2)*1220,115+(i//2)*485))
 d.text((30,1080),'R45 Daytona excludes separate R46/R47. Source-only views; not calibrated game-driver camera.',font=foot,fill='#A8B1BA')
 overview_file=D/'00_FERRARI_4_MODELS_REAL_MESH_DETAIL_COMPARISON.png'
 overview.save(overview_file,optimize=True)
 manifest['overview_sha256']=sha(overview_file)
 (D/'manifest_detail.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
 from zipfile import ZipFile,ZIP_DEFLATED
 zipfile=D/'FERRARI_4_CARS_ACTUAL_MODEL_DETAIL_COMPARISON_20261110.zip'
 with ZipFile(zipfile,'w',ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(D.glob('*_REAL_ORIGINAL_VS_FINAL_*.png')):z.write(p,arcname=p.name)
  z.write(overview_file,arcname=overview_file.name)
  z.write(D/'manifest_detail.json',arcname='manifest_detail.json')
 print('DETAIL_OVERVIEW_READY',sha(overview_file),zipfile.stat().st_size,flush=True)
def run():
 for car,c in CASES.items():
  for stage in ['before','after']:
   assert c[stage].exists() and sha(c[stage])==c[stage+'_sha'],car+stage
 for car,c in CASES.items():
  for reg in c['cases']:
   for stage in ['before','after']:
    dst=D/(car+'_'+reg+'_native_'+stage+'.png')
    p=subprocess.run([str(BLENDER),'-b',str(c[stage]),'-t','2','--python',str(Path(__file__).resolve()),'--',
      car,stage,reg,str(dst)],capture_output=True,text=True,timeout=90)
    ok=[x for x in p.stdout.splitlines() if x.startswith('NATIVE_COMPONENT_CAPTURE_OK')]
    if not ok or p.returncode:raise RuntimeError(car+stage+reg+' '+p.stdout[-1100:]+' '+p.stderr[-500:])
    print(ok[-1],flush=True)
 layout()
 assert all(sha(c[k])==c[k+'_sha'] for c in CASES.values() for k in ('before','after'))
 print('ALL_BLENDS_UNCHANGED',flush=True)
if __name__=='__main__':
 if '--' in sys.argv:blender()
 else:run()