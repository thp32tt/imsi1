#!/usr/bin/env python3
"""Inspection only: original F355 Spider PMT-derived seat isolated from other meshes."""
from pathlib import Path
import sys, subprocess, json, collections
ROOT=Path("/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-visibleseat-20261110")
BLEND=ROOT/"artifacts/slot_C/f355spider/center_console_v1/F355Spider_OriginalPMT_CenterConsole_GateBezel_v1.blend"
BLENDER="/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender"
OUT=Path("/home/chatgpt-runner/tmp/f355_seat_probe_20261110")
TARGET="PMT_F355SPIDER_object00_group01_material027_a0"
def inspect():
 import bpy
 from mathutils import Vector
 s=bpy.context.scene; OUT.mkdir(exist_ok=True,parents=True)
 allobjects={o.name:o for o in bpy.data.objects if o.type=="MESH"}
 assert len(allobjects)==96 and TARGET in allobjects
 ob=allobjects[TARGET];m=ob.data
 par=list(range(len(m.vertices)))
 def find(i):
  while par[i]!=i:par[i]=par[par[i]];i=par[i]
  return i
 for f in m.polygons:
  a=f.vertices[0]
  for b in f.vertices[1:]:par[find(a)]=find(b)
 comp=collections.defaultdict(list)
 for v in m.vertices:comp[find(v.index)].append(v.index)
 report=[]
 for ids in comp.values():
  pts=[m.vertices[i].co for i in ids]
  a={k:{"min":min(float(p[k]) for p in pts),"max":max(float(p[k]) for p in pts),"mean":sum(float(p[k]) for p in pts)/len(pts)} for k in range(3)}
  report.append({"vertices":len(ids),"indices":ids,"bounds":a})
 print("SEAT_NATIVE_COMPONENTS",json.dumps(report),flush=True)
 s.render.engine="BLENDER_WORKBENCH";s.render.resolution_x=1100;s.render.resolution_y=710;s.render.resolution_percentage=100
 s.render.image_settings.file_format="PNG";s.display.shading.color_type="OBJECT";s.display.shading.light="STUDIO";s.display.shading.show_cavity=True
 camdata=bpy.data.cameras.new("temporary_seat_probe");cam=bpy.data.objects.new("temporary_seat_probe",camdata);s.collection.objects.link(cam);s.camera=cam;camdata.type="ORTHO";camdata.ortho_scale=1.85
 positions=[
  ("front_angled",(1.50,1.50,-1.55),(0.33,.53,.03)),
  ("rear_angled",(1.6,1.50,1.48),(0.32,.53,.02)),
  ("left_front",(-1.65,1.44,-1.4),(-.30,.53,.03)),
  ("top_down",(-0.6,2.7,-.55),(-.24,.45,.01)),
  ("side",(1.8,.96,.22),(.30,.50,.01))
 ]
 for mode in ("seat_only","all"):
  for o in allobjects.values():
   o.hide_render=(mode=="seat_only" and o.name!=TARGET)
   o.color=(.42,.69,.89,1) if o.name==TARGET else (.59,.59,.60,1)
  for name,pos,look in positions:
   cam.location=pos;cam.rotation_euler=(Vector(look)-cam.location).to_track_quat("-Z","Y").to_euler()
   s.render.filepath=str(OUT/(mode+"_"+name+".png"))
   bpy.ops.render.render(write_still=True)
   print("RENDER",s.render.filepath,flush=True)
 print("DONE_SEAT_INSPECTION",flush=True)
if "--" in sys.argv and sys.argv[-1]=="inside": inspect()
else:
 p=subprocess.run([BLENDER,"--background","-noaudio","-t","2",str(BLEND),"--python",str(Path(__file__).resolve()),"--","inside"],text=True,capture_output=True,timeout=160,cwd=str(ROOT))
 print(p.stdout[-16500:]);print(p.stderr[-1500:],file=sys.stderr);sys.exit(p.returncode)
