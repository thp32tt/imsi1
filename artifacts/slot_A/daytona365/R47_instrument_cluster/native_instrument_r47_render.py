#!/usr/bin/env python3
"""Blender 4.5.15 read-only exact-camera before-after instrument cluster render."""
import sys,subprocess,hashlib,json
from pathlib import Path
ROOT=Path("/home/chatgpt-runner")
DIR=ROOT/"worktrees/imsi1-slotA-instrument-20261109-1303/artifacts/slot_A/daytona365/R47_instrument_cluster"
BL=ROOT/"work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender"
ORIG=ROOT/"work_handoff/daytona365_rework_20261107/original_game_blender/Daytona365_ORIGINAL_GAME_COCKPIT_COMPARE.blend"
AFTER=DIR/"Daytona365_NATIVE_PMT015_InstrumentCluster_R47.blend"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for a in iter(lambda:f.read(1048576),b""):h.update(a)
 return h.hexdigest()
try:import bpy
except ImportError:bpy=None
if bpy is None:
 for stage,src in (("before",ORIG),("after",AFTER)):
  p=subprocess.run([str(BL),"--background",str(src),"--threads","1","--python",str(Path(__file__).resolve()),"--","--inside-"+stage],capture_output=True,text=True,timeout=175)
  print(stage,p.returncode,p.stdout[-2500:],p.stderr[-2000:],flush=True)
  if p.returncode or not (DIR/("PMT015_"+stage+"_workbench.png")).exists():raise RuntimeError("RENDER_FAILED_"+stage)
 from PIL import Image,ImageDraw,ImageChops
 imgs=[Image.open(DIR/("PMT015_"+s+"_workbench.png")).convert("RGB") for s in ("before","after")]
 w,h=imgs[0].size
 combined=Image.new("RGB",(w*2,h+42),(25,27,31));d=ImageDraw.Draw(combined)
 for i,(im,t) in enumerate(zip(imgs,("Native PMT015 - Original","Native PMT015 - R47 Gauge Bezel"))):
  combined.paste(im,(i*w,42));d.text((i*w+14,12),t,fill=(245,245,245))
 out=DIR/"Daytona365_NATIVE_PMT015_R47_BeforeAfter.png";combined.save(out,optimize=True)
 delta=ImageChops.difference(imgs[0],imgs[1])
 changed=sum(1 for r,g,b in delta.getdata() if max(r,g,b)>3)
 q={"render":"BLENDER_4_5_15_REAL_WORKBENCH_SAME_CAMERA","camera":"(-.56,-.66,1.11) to (-.345,.175,.825) orthographic .74",
  "before_original_blend_sha256":sha(ORIG),"after_original_derived_blend_sha256":sha(AFTER),
  "changed_pixels_max_RGB_gt_3":changed,"before_png_sha256":sha(DIR/"PMT015_before_workbench.png"),
  "after_png_sha256":sha(DIR/"PMT015_after_workbench.png"),"comparison_png_sha256":sha(out),
  "not_a_genuine_game_camera":True,"authentic_reference_photos_remain_private":True,"full_car_qa_pass":False}
 (DIR/"native_instrument_r47_render_qa.json").write_text(json.dumps(q,indent=2)+"\n")
 print("RENDER_EVIDENCE",json.dumps(q),flush=True)
 sys.exit(0)
from mathutils import Vector
sc=bpy.context.scene
for ob in bpy.data.objects:
 if ob.type=="MESH":
  ob.hide_render=ob.name not in ("object00_group01_material014_a0","object00_group01_material015_a0")
cam_d=bpy.data.cameras.new("TEMP_ONLY_RENDER_CAMERA")
cam=bpy.data.objects.new("TEMP_ONLY_RENDER_CAMERA",cam_d);sc.collection.objects.link(cam)
cam.location=(-.56,-.66,1.11);aim=Vector((-.345,.175,.825))
cam.rotation_euler=(aim-cam.location).to_track_quat("-Z","Y").to_euler()
cam_d.type="ORTHO";cam_d.ortho_scale=.74;sc.camera=cam
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.light="STUDIO";sc.display.shading.studio_light="paint.sl"
sc.display.shading.color_type="SINGLE";sc.display.shading.single_color=(.48,.54,.6)
sc.display.shading.show_cavity=True;sc.display.shading.cavity_type="BOTH"
sc.display.shading.show_shadows=True
sc.render.resolution_x=900;sc.render.resolution_y=600;sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.render.filepath=str(DIR/("PMT015_"+("before" if "--inside-before" in sys.argv else "after")+"_workbench.png"))
bpy.ops.render.render(write_still=True)
print("RENDER_DONE",sc.render.filepath)