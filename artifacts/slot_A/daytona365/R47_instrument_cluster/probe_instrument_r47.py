#!/usr/bin/env python3
import sys,json,subprocess,hashlib
from pathlib import Path
ROOT=Path("/home/chatgpt-runner")
BL=ROOT/"work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender"
ORIG=ROOT/"work_handoff/daytona365_rework_20261107/original_game_blender/Daytona365_ORIGINAL_GAME_COCKPIT_COMPARE.blend"
OUT=ROOT/"worktrees/imsi1-slotA-instrument-20261109-1303/artifacts/slot_A/daytona365/native_instrument_inventory_r47.json"
if "--inside" not in sys.argv:
 p=subprocess.run([str(BL),"--background",str(ORIG),"--threads","1","--python",str(Path(__file__).resolve()),"--","--inside"],capture_output=True,text=True,timeout=100)
 print("exit",p.returncode,"stdout",p.stdout[-2000:],"stderr",p.stderr[-2000:])
 sys.exit(p.returncode)
import bpy
items=[]
for o in bpy.data.objects:
 if o.type!="MESH":continue
 m=o.data
 vs=[o.matrix_world@v.co for v in m.vertices]
 if not vs:continue
 lo=[round(min(v[i] for v in vs),4) for i in range(3)]
 hi=[round(max(v[i] for v in vs),4) for i in range(3)]
 mats=[x.name if x else "" for x in m.materials]
 # vertex adjacency connected components
 parent=list(range(len(vs)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for edge in m.edges:
  a,b=edge.vertices
  pa,pb=find(a),find(b)
  if pa!=pb:parent[pa]=pb
 cc={}
 for v in m.vertices:cc.setdefault(find(v.index),[]).append(v.index)
 cmps=[]
 for ids in cc.values():
  if len(ids)<3:continue
  xyz=[vs[i] for i in ids]
  cmps.append({"n":len(ids),"range":[[round(min(v[j] for v in xyz),4),round(max(v[j] for v in xyz),4)] for j in range(3)],"ids":ids[:15]})
 cmps=sorted(cmps,key=lambda x:-x["n"])
 items.append({"name":o.name,"n":len(vs),"f":len(m.polygons),"lo":lo,"hi":hi,"materials":mats,"components":cmps[:60]})
OUT.write_text(json.dumps(items,indent=2)+"\n")
print("NATIVE_INVENTORY",len(items),OUT)