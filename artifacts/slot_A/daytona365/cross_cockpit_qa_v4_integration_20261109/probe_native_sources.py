#!/usr/bin/env python3
"""Read-only native source object fingerprints for Daytona R45/R46/R47/original."""
import hashlib, json, os, struct, subprocess, sys
from pathlib import Path
REL="artifacts/slot_A/daytona365/cross_cockpit_qa_v4_integration_20261109"
ROOT=Path("/home/chatgpt-runner")
REPO=ROOT/"imsi1_slotA_crossqa_20261109"
BINARY=ROOT/"work_handoff/daytona365_rework_20261107/blender-4.5.15-linux-x64/blender"
SCENES={
"R45":ROOT/"work_handoff/ferrari16_slotA_daytona_dashboard_steering_20261108/Daytona365_SlotA_OriginalPMT005_InnerDoor_R45.blend",
"R46":REPO/"artifacts/slot_A/daytona365/R46_visible_seat/Daytona365_NATIVE_PMT017_VisibleSeat_R46.blend",
"R47":REPO/"artifacts/slot_A/daytona365/R47_instrument_cluster/Daytona365_NATIVE_PMT015_InstrumentCluster_R47.blend",
"ORIGINAL":ROOT/"work_handoff/daytona365_rework_20261107/original_game_blender/Daytona365_ORIGINAL_GAME_COCKPIT_COMPARE.blend",
}
OUT=REPO/REL
def digest(path):
  h=hashlib.sha256()
  with open(path,"rb") as f:
    for ch in iter(lambda:f.read(1048576),b""):h.update(ch)
  return h.hexdigest()
def child(src,dst):
  import bpy
  bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False)
  def fingerprint(obj):
    mesh=obj.data
    h=hashlib.sha256()
    for v in mesh.vertices:h.update(struct.pack("<3d",*v.co))
    for p in mesh.polygons:
      h.update(struct.pack("<I",len(p.vertices)))
      for i in p.vertices:h.update(struct.pack("<I",i))
    return h.hexdigest()
  objs={}
  for obj in bpy.data.objects:
    if obj.type=="MESH":
      inf={"vertex_count":len(obj.data.vertices),"face_count":len(obj.data.polygons),
      "mesh_sha256":fingerprint(obj),"mesh_datablock":obj.data.name,
      "matrix_world":[round(x,8) for row in obj.matrix_world for x in row],
      "hide_render":bool(obj.hide_render),"hide_viewport":bool(obj.hide_viewport)}
      if ("material015" in obj.name.lower() or "material017" in obj.name.lower() or "seat" in obj.name.lower() or "gauge" in obj.name.lower() or "instrument" in obj.name.lower()):inf["bounds"]=[[round(x,5) for x in corner] for corner in obj.bound_box]
      objs[obj.name]=inf
  cam=[{"name":o.name,"matrix_world":[round(x,6) for row in o.matrix_world for x in row],"camera_lens":round(o.data.lens,4)} for o in bpy.data.objects if o.type=="CAMERA"]
  record={"source_file":str(src),"source_sha256":digest(src),"blender_version":bpy.app.version_string,
    "native_objects":{k:v for k,v in objs.items() if k.startswith("object")},
    "target_related":{k:v for k,v in objs.items() if any(s in k.lower() for s in ["material015","material017","seat","gauge","instrument"])},
    "cameras":cam,"all_mesh_count":len(objs),"all_mesh_sha256":hashlib.sha256(json.dumps({k:v["mesh_sha256"] for k,v in sorted(objs.items())},sort_keys=True).encode()).hexdigest()}
  dst.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
  print("INSPECT",src.name,"MESH",len(objs),"NATIVE",len(record["native_objects"]),"CAM",len(cam))
if __name__=="__main__":
  if "--child" in sys.argv:
    i=sys.argv.index("--child");child(Path(sys.argv[i+1]),Path(sys.argv[i+2]))
  else:
    OUT.mkdir(parents=True,exist_ok=True)
    for label,src in SCENES.items():
      dst=OUT/("probe_"+label+".json")
      result=subprocess.run([str(BINARY),"-b","-noaudio","--python",str(Path(__file__).resolve()),"--","--child",str(src),str(dst)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True,timeout=110,env={**os.environ,"BLENDER_USER_CONFIG":"/tmp/ferrari_slotA_probe_config","OMP_NUM_THREADS":"2"})
      print(label,"exit",result.returncode,result.stdout[-2400:])
      if result.returncode or not dst.exists():raise SystemExit("FAILED "+label)
    r={s:json.loads((OUT/("probe_"+s+".json")).read_text()) for s in SCENES}
    names=["object00_group01_material017_a0","object00_group01_material015_a0"]
    for s,inf in r.items():
      print("SOURCE",s,"SHA",inf["source_sha256"],"CAM",len(inf["cameras"]),"MESHES",inf["all_mesh_count"])
      for name in names: print("OBJECT",s,name,inf["native_objects"].get(name))
      print("TARGET_MATCHING",s,[k for k in inf["target_related"] if any(w in k.lower() for w in ("seat","gauge","instrument"))][:50])