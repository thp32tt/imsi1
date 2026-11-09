from pathlib import Path
import sys,collections,math,json
sys.path.insert(0,"/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-innerdoor-20261110/tools/car_modeling/slot_c")
from f355spider_native_pmt_reader import open_pmt,decode_object
P=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f355sp_pmt.sz")
A=open_pmt(P)
res=[]
for p in decode_object(A,0):
 vs=p["vertices"]; inds=p["indices"]
 stat=collections.Counter();faces_sample=[]
 for j in range(0,len(inds),3):
  a,b,c=(vs[i] for i in inds[j:j+3])
  cen=[sum(v[k] for v in (a,b,c))/3 for k in range(3)]
  if not(-.95<cen[0]<-.66 and .22<cen[1]<.85 and -.7<cen[2]<.7):continue
  ab=[b[k]-a[k] for k in range(3)]; ac=[c[k]-a[k] for k in range(3)]
  nx=ab[1]*ac[2]-ab[2]*ac[1]
  key="inward" if nx>0.0001 else ("outward" if nx<-.0001 else "parallel")
  stat[key]+=1
  if len(faces_sample)<12:faces_sample.append([round(z,3) for z in cen]+[round(nx,5)])
 if stat:
  res.append(dict(part=p["name"],n_verts=len(vs),n_faces=len(inds)//3,region_faces=sum(stat.values()),normals=dict(stat),sample=faces_sample))
print(json.dumps(res,indent=2))
