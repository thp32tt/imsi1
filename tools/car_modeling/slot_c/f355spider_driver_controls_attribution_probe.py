import subprocess,sys
from pathlib import Path
ROOT=Path("/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-drivercontrols-20261110")
BLEND=ROOT/"artifacts/slot_C/f355spider/center_console_v1/F355Spider_OriginalPMT_CenterConsole_GateBezel_v1.blend"
BLENDER="/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender"
OUT=Path("/home/chatgpt-runner/tmp/f355_driver_controls_select_20261110")
def inside():
 import bpy
 from mathutils import Vector
 scene=bpy.context.scene
 scene.render.engine="BLENDER_WORKBENCH";scene.render.resolution_x=1050;scene.render.resolution_y=720;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format="PNG";scene.display.shading.color_type="OBJECT"
 camdat=bpy.data.cameras.new("qa_close_camera");cam=bpy.data.objects.new("qa_close_camera",camdat);scene.collection.objects.link(cam);scene.camera=cam
 camdat.type="PERSP";camdat.lens=39
 views=[("driver",(-0.35,0.86,0.15),(-0.35,0.60,-0.79)),("left",(-0.63,0.82,-0.22),(-0.35,0.64,-0.68)),("center",(0.0,0.93,0.04),(-0.28,0.65,-0.7))]
 series=[("cluster011",["material011"]),("cluster016",["material016"]),("clusterboth",["material011","material016"]),("clusterother",["material011","material016","material019","material018","material023"])]
 for title,names in series:
  for o in bpy.data.objects:
   o.hide_render=o.type!="MESH" or not any(s in o.name for s in names) or "object00_" not in o.name
   o.color=(.60,.70,.85,1) if "material011" in o.name else (.80,.48,.50,1) if "material016" in o.name else (.87,.75,.35,1)
  for view,loc,pt in views:
   cam.location=loc;cam.rotation_euler=(Vector(pt)-cam.location).to_track_quat("-Z","Y").to_euler()
   scene.render.filepath=str(OUT/(title+"_"+view+".png"));bpy.ops.render.render(write_still=True)
   print("IMAGE",title,view,flush=True)
if sys.argv[-1]=="internal":inside()
else:
 p=subprocess.run([BLENDER,"--background","-noaudio","-t","2",str(BLEND),"--python",str(Path(__file__).resolve()),"--","internal"],cwd=str(ROOT),capture_output=True,text=True,timeout=180)
 print(p.stdout[-2000:]);print(p.stderr[-1000:]);sys.exit(p.returncode)
