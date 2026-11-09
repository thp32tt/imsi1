#!/usr/bin/env python3
"""Read-only native PMT door ROI / connected component inventory."""
import bpy, json, hashlib, struct, collections
from pathlib import Path
root=Path(__file__).resolve().parents[2]
src=root/"artifacts/slot_A/360spider/center_console_20261110/Ferrari360Spider_CenterConsole_SourceEdit_R01.blend"
assert src.is_file()
bpy.ops.wm.open_mainfile(filepath=str(src))
D=[]
for obj in sorted([x for x in bpy.data.objects if x.type=="MESH"],key=lambda x:x.name):
    m=obj.data
    n=len(m.vertices)
    if not obj.name.startswith("PMT_object00_"):continue
    parent=list(range(n))
    def find(a):
        while parent[a]!=a:
            parent[a]=parent[parent[a]]
            a=parent[a]
        return a
    def union(a,b):
        aa,bb=find(a),find(b)
        if aa!=bb: parent[bb]=aa
    for f in m.polygons:
        vs=f.vertices
        for v in vs[1:]:union(vs[0],vs[0])
        for v in vs[1:]:union(vs[0],v)
    components=collections.defaultdict(list)
    for v in m.vertices:components[find(v.index)].append(v.index)
    for IDs in components.values():
        vs=[m.vertices[i].co for i in IDs]
        xs=[v.x for v in vs];ys=[v.y for v in vs];zs=[v.z for v in vs]
        roi=[i for i in IDs if abs(m.vertices[i].co.x)>.67 and .17<m.vertices[i].co.y<1.04 and -1.4<m.vertices[i].co.z<1.15]
        if len(roi)<3:continue
        row=dict(mesh=obj.name,n=len(IDs),roi_n=len(roi),root=min(IDs),
          min=[round(min(c),4) for c in (xs,ys,zs)],max=[round(max(c),4) for c in (xs,ys,zs)],
          center=[round(sum(c)/len(c),4) for c in (xs,ys,zs)],sample_ids=roi[:18],
          driverside=sum(1 for i in roi if m.vertices[i].co.x<-.67),
          otherside=sum(1 for i in roi if m.vertices[i].co.x>.67),
          near_windshield=sum(1 for i in IDs if abs(m.vertices[i].co.x)>.65 and m.vertices[i].co.y>.75 and m.vertices[i].co.z<-.83),
          door_low=sum(1 for i in IDs if abs(m.vertices[i].co.x)>.70 and .23<m.vertices[i].co.y<.73 and -.72<m.vertices[i].co.z<.70),
          )
        D.append(row)
D.sort(key=lambda x:(-x['door_low'],-x['roi_n']))
out=root/"artifacts/slot_A/360spider/inner_door_20261110"
out.mkdir(parents=True,exist_ok=True)
(out/"native_door_roi_inventory.json").write_text(json.dumps({"read_only":True,"source":str(src),"components":D},indent=2))
print(json.dumps(D[:70],ensure_ascii=False),flush=True)