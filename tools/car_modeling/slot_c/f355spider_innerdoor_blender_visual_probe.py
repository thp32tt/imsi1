from pathlib import Path
import subprocess,sys
R=Path("/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-innerdoor-20261110")
B=R/"artifacts/slot_C/f355spider/center_console_v1/F355Spider_OriginalPMT_CenterConsole_GateBezel_v1.blend"
BL="/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender"
OUT=Path("/home/chatgpt-runner/tmp/f355_innerdoor_visual_20261110")
def run():
 import bpy
 from mathutils import Vector
 OUT.mkdir(parents=True,exist_ok=True)
 s=bpy.context.scene
 s.render.engine="BLENDER_WORKBENCH";s.render.resolution_x=1000;s.render.resolution_y=640;s.render.resolution_percentage=100
 s.render.image_settings.file_format="PNG";s.display.shading.color_type="OBJECT";s.display.shading.light="STUDIO";s.display.shading.show_shadows=True
 camdat=bpy.data.cameras.new("diagnostic_camera");cam=bpy.data.objects.new("diagnostic_camera",camdat);s.collection.objects.link(cam);s.camera=cam
 camdat.type="ORTHO";camdat.ortho_scale=2.75
 objs=[o for o in bpy.data.objects if o.type=="MESH"]
 looks=[("driver_left",(-1.55,1.30,-1.40),(-0.40,0.53,0.36)),("interior_left",(-1.8,1.15,0.10),(-0.40,0.49,0.0)),("interior_right",(1.8,1.15,0.10),(0.40,0.49,0.0))]
 cases=[("all",None),("door_candidates",["material005","material024","material026","material031"]),("door_026",["material026"]),("door_024",["material024"]),("door_005",["material005"])]
 for case,subset in cases:
  for o in objs:
   n=o.name
   o.hide_render=False if subset is None else not (n.startswith("PMT_F355SPIDER_object00_") and any(t in n for t in subset))
   o.color=(.65,.69,.76,1) if subset is None else ((.9,.3,.16,1) if "material026" in n else (.2,.68,.96,1) if "material024" in n else (.28,.74,.3,1) if "material031" in n else (.67,.65,.66,1))
  for v,loc,at in looks if case in ("all","door_candidates") else looks[1:]:
   cam.location=loc;cam.rotation_euler=(Vector(at)-cam.location).to_track_quat("-Z","Y").to_euler()
   s.render.filepath=str(OUT/f"{case}_{v}.png")
   bpy.ops.render.render(write_still=True)
   print("PNG",s.render.filepath,flush=True)
 print("ALL_DONE",flush=True)
if "--" in sys.argv and sys.argv[-1]=="inside":run()
else:
 assert B.is_file()
 p=subprocess.run([BL,"-b","-t","2",str(B),"--python",str(Path(__file__).resolve()),"--","inside"],cwd=str(R),text=True,capture_output=True,timeout=240)
 print(p.stdout[-3000:]);print(p.stderr[-1200:],file=sys.stderr);sys.exit(p.returncode)
