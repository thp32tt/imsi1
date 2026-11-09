#!/usr/bin/env python3
"""Read-only matched-camera Blender 4.5.15 Workbench comparison of native PMT017 seats.
No texture/material/geometry changes are saved to either BLEND.
"""
import sys,subprocess,json,hashlib
from pathlib import Path
DIR=Path("/home/chatgpt-runner/worktrees/imsi1-slotA-visible-seat-20261109/artifacts/slot_A/daytona365/R46_visible_seat")
BL=Path("/home/chatgpt-runner/.cache/f50_slotc_blender_4_5_15/blender-4.5.15-linux-x64/blender")
ORIG=Path("/home/chatgpt-runner/work_handoff/daytona365_rework_20261107/original_game_blender/Daytona365_ORIGINAL_GAME_COCKPIT_COMPARE.blend")
OUT=DIR/"Daytona365_NATIVE_PMT017_VisibleSeat_R46.blend"
TARGET="object00_group01_material017_a0"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb")as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
try:import bpy
except ImportError:bpy=None
if bpy is None:
 for stage,src in [("before",ORIG),("after",OUT)]:
  p=subprocess.run([str(BL),"--background",str(src),"--threads","1","--python",str(Path(__file__).resolve()),"--","--inside-"+stage],capture_output=True,text=True,timeout=190)
  print("RENDER_"+stage.upper(),p.stdout[-4000:],p.stderr[-1600:],flush=True)
  path=DIR/("PMT017_"+stage+"_workbench.png")
  if p.returncode or "Traceback" in p.stderr or not path.is_file():raise RuntimeError("BLOCKED_RENDER_"+stage)
 from PIL import Image,ImageDraw,ImageChops
 imgs=[Image.open(DIR/("PMT017_"+s+"_workbench.png")).convert("RGB") for s in ("before","after")]
 w,h=imgs[0].size
 canvas=Image.new("RGB",(w*2,h+45),(24,27,31))
 dr=ImageDraw.Draw(canvas)
 for i,(im,label) in enumerate(zip(imgs,["Original PMT017 - Before","Original PMT017 - R46 Native Geometry"])):
  canvas.paste(im,(i*w,45));dr.text((i*w+16,14),label,fill=(243,245,246))
 comp=DIR/"Daytona365_NATIVE_PMT017_R45Ref_R46_BeforeAfter.png"
 canvas.save(comp,optimize=True)
 diff=ImageChops.difference(imgs[0],imgs[1])
 from PIL import ImageStat
 changed=sum(1 for r,g,b in diff.getdata() if max(r,g,b)>3)
 proof={"comparison_type":"real_blender_4_5_15_workbench_same_orthographic_camera",
 "view":"angled_seat_only","before_original_import_sha256":sha(ORIG),
 "after_r46_blend_sha256":sha(OUT),"before_image_sha256":sha(DIR/"PMT017_before_workbench.png"),
 "after_image_sha256":sha(DIR/"PMT017_after_workbench.png"),
 "comparison_image_sha256":sha(comp),"pixels_changed_rgb_max_gt_3":changed,
 "camera":"(1.48,1.15,1.22)->(0,-0.34,0.55) ortho 1.67",
 "actual_game_driver_eye_calibrated":False,"photo_reference_not_republished":True}
 (DIR/"native_seat_r46_render_qa.json").write_text(json.dumps(proof,indent=2)+"\n",encoding="utf-8")
 print("RENDER_COMPARISON",json.dumps(proof),flush=True)
 sys.exit(0)
from mathutils import Vector
obj=bpy.data.objects[TARGET]
for o in bpy.data.objects:
 if o.type=="MESH" and o.name!=TARGET:o.hide_render=True
obj.hide_render=False
sc=bpy.context.scene
cam_data=bpy.data.cameras.new("TEMP_RENDER_ONLY_CAMERA")
cam=bpy.data.objects.new("TEMP_RENDER_ONLY_CAMERA",cam_data)
sc.collection.objects.link(cam)
cam.location=(1.48,1.15,1.22)
target=Vector((0,-.34,.55))
cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.type="ORTHO";cam.data.ortho_scale=1.67
sc.camera=cam
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.light="STUDIO"
sc.display.shading.studio_light="paint.sl"
sc.display.shading.color_type="SINGLE"
sc.display.shading.single_color=(0.76,0.47,0.26)
sc.display.shading.show_cavity=True
sc.display.shading.cavity_type="BOTH"
sc.display.shading.show_shadows=True
sc.render.resolution_x=960;sc.render.resolution_y=600;sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.render.film_transparent=False
sc.render.filepath=str(DIR/("PMT017_"+("before" if "--inside-before" in sys.argv else "after")+"_workbench.png"))
bpy.ops.render.render(write_still=True)
print("RENDER_SAVED",sc.render.filepath)