#!/usr/bin/env python3
import bpy,json,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
src=ROOT/"artifacts/slot_A/360spider/center_console_20261110/Ferrari360Spider_CenterConsole_SourceEdit_R01.blend"
out=ROOT/"artifacts/slot_A/360spider/visible_seat_20261110"
bpy.ops.wm.open_mainfile(filepath=str(src))
o=bpy.data.objects["PMT_object00_group01_material010_a0"]
m=o.data;n=len(m.vertices);p=list(range(n))
def find(i):
 while p[i]!=i:p[i]=p[p[i]];i=p[i]
 return i
def union(a,b):
 a=find(a);b=find(b)
 if a!=b:p[a]=b
for face in m.polygons:
 ids=list(face.vertices)
 for v in ids[1:]:union(ids[0],v)
groups=collections.defaultdict(list)
for v in m.vertices:groups[find(v.index)].append(v.index)
stats=[]
for i,inds in enumerate(groups.values()):
 a=[[m.vertices[j].co[k] for j in inds] for k in range(3)]
 lo=[min(c) for c in a];hi=[max(c) for c in a];ct=[sum(c)/len(c) for c in a]
 stat={"root":min(inds),"n":len(inds),"lo":[round(q,4) for q in lo],"hi":[round(q,4) for q in hi],"center":[round(q,4) for q in ct],"ids":inds,"left":sum(1 for j in inds if m.vertices[j].co.x<-.22),"right":sum(1 for j in inds if m.vertices[j].co.x>.22)}
 stats.append(stat)
stats.sort(key=lambda s:(-s["n"],s["root"]))
(out/"material010_connected_islands.json").write_text(json.dumps({"target":o.name,"total_vertices":n,"total_components":len(stats),"components":stats},indent=2)+"\n")
print("COMPONENTS",len(stats),"major first",json.dumps([{k:v for k,v in r.items() if k!="ids"} for r in stats[:130]]),flush=True)