from pathlib import Path
import subprocess,sys
R=Path("/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-innerdoor-20261110")
B=R/"artifacts/slot_C/f355spider/center_console_v1/F355Spider_OriginalPMT_CenterConsole_GateBezel_v1.blend"
BL="/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender"
OUT=Path("/home/chatgpt-runner/tmp/f355_innerdoor_detail_20261110")
def run():
 import bpy,collections
 from mathutils import Vector
 OUT.mkdir(parents=True,exist_ok=True)
 s=bpy.context.scene;s.render.engine="BLENDER_WORKBENCH";s.render.resolution_x=1000;s.render.resolution_y=650;s.render.resolution_percentage=100
 s.render.image_settings.file_format="PNG";s.display.shading.color_type="OBJECT"
 camdata=bpy.data.cameras.new("diagnostic_inside");cam=bpy.data.objects.new("diagnostic_inside",camdata);s.collection.objects.link(cam);s.camera=cam;camdata.type="ORTHO";camdata.ortho_scale=1.68
 objs=[o for o in bpy.data.objects if o.type=="MESH"]
 for o in objs:o.hide_render=True
 components=[("001_31","PMT_F355SPIDER_object00_group00_material001_a0",197,(1,.55,.1,1)),
             ("005_22","PMT_F355SPIDER_object00_group01_material005_a0",2463,(.25,.9,.45,1)),
             ("005_32","PMT_F355SPIDER_object00_group01_material005_a0",2308,(.20,.5,.95,1)),
             ("024_4","PMT_F355SPIDER_object00_group01_material024_a0",4,(1,.2,.7,1))]
 created=[]
 for label,objname,anchor,color in components:
  src=bpy.data.objects[objname]
  n=len(src.data.vertices);parent=list(range(n))
  def f(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  for p in src.data.polygons:
   vs=p.vertices
   for i in range(1,len(vs)):parent[f(vs[i])]=f(vs[0])
  target=f(anchor)
  faces=[p for p in src.data.polygons if f(p.vertices[0])==target]
  old=sorted({idx for p in faces for idx in p.vertices});mp={v:i for i,v in enumerate(old)}
  mesh=bpy.data.meshes.new(label+"_qa");mesh.from_pydata([tuple(src.data.vertices[i].co) for i in old],[],[tuple(mp[i] for i in p.vertices) for p in faces]);mesh.update()
  o=bpy.data.objects.new(label+"_qa",mesh);s.collection.objects.link(o);o.color=color;created.append(o)
  print("COMP",label,len(old),len(faces),[tuple(round(min(src.data.vertices[i].co[k] for i in old),3) for k in range(3)),tuple(round(max(src.data.vertices[i].co[k] for i in old),3) for k in range(3))],flush=True)
 views=[("from_center",(-.10,.91,-.62),(-.87,.48,-.55)),("door_side",(.18,.80,-.58),(-.85,.47,-.5)),("from_rear",(-.02,.90,-1.2),(-.82,.43,-.51))]
 for subset in [["001_31"],["005_22"],["005_32"],["001_31","005_22","005_32","024_4"]]:
  for o in created:o.hide_render=o.name.split("_qa")[0] not in subset
  label="+".join(subset)
  for v,loc,at in views:
   cam.location=loc;cam.rotation_euler=(Vector(at)-cam.location).to_track_quat("-Z","Y").to_euler()
   s.render.filepath=str(OUT/f"{label}_{v}.png")
   bpy.ops.render.render(write_still=True)
   print("PNG",s.render.filepath,flush=True)
if "--" in sys.argv and sys.argv[-1]=="inside":run()
else:
 p=subprocess.run([BL,"-b","-t","2",str(B),"--python",str(Path(__file__).resolve()),"--","inside"],text=True,capture_output=True,timeout=180)
 print(p.stdout[-5000:]);print(p.stderr[-900:],file=sys.stderr);sys.exit(p.returncode)
