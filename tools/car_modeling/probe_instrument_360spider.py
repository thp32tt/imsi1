#!/usr/bin/env python3
import bpy,json,math,collections,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/slot_A/360spider/visible_seat_20261110/Ferrari360Spider_VisibleSeat_OriginalPMT_R02.blend"
OUT=ROOT/"artifacts/slot_A/360spider/instrument_cluster_20261110"
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SRC))
def stat(idxs, verts):
 c=[verts[i].co for i in idxs]
 return {"n":len(idxs),"lo":[round(min(v[j] for v in c),4) for j in range(3)],"hi":[round(max(v[j] for v in c),4) for j in range(3)],"center":[round(sum(v[j] for v in c)/len(c),4) for j in range(3)]}
out=[]
for obj in sorted((o for o in bpy.data.objects if o.type=="MESH"), key=lambda o:o.name):
 m=obj.data; d=stat(range(len(m.vertices)),m.vertices)
 d.update(name=obj.name,faces=len(m.polygons),mats=[t.name for t in m.materials if t])
 out.append(d)
(OUT/"native_object_bounds.json").write_text(json.dumps(out,indent=2)+"\n")
islands=[]
for ob in [o for o in bpy.data.objects if o.type=="MESH" and o.name.startswith("PMT_object00_")]:
 m=ob.data;parent=list(range(len(m.vertices)))
 def root(a):
  while parent[a]!=a:
   parent[a]=parent[parent[a]];a=parent[a]
  return a
 def join(a,b):
  a=root(a);b=root(b)
  if a!=b:parent[b]=a
 for p in m.polygons:
  a=p.vertices[0]
  for v in p.vertices[1:]:join(a,v)
 parts=collections.defaultdict(list)
 for v in m.vertices:parts[root(v.index)].append(v.index)
 for key,ids in parts.items():
  if len(ids)<3:continue
  d=stat(ids,m.vertices); d.update(object=ob.name,index_min=min(ids),index_max=max(ids),vertex_indices=ids if len(ids)<=90 else [],face_count=sum(1 for p in m.polygons if root(p.vertices[0])==key))
  islands.append(d)
(OUT/"native_islands.json").write_text(json.dumps(sorted(islands,key=lambda x:(x["object"],-x["n"])),indent=2)+"\n")
print("OBJECTS",len(out),"ISLANDS",len(islands),flush=True)
for o in out:
 if o["name"].startswith("PMT_object00_"):print("OBJECT",o["name"],o["n"],o["lo"],o["hi"],flush=True)
for i in sorted(islands,key=lambda x:(x["object"],-x["n"])):
 if i["n"]>=9:print("ISLAND",i["object"],i["n"],i["index_min"],i["center"],i["lo"],i["hi"],flush=True)
