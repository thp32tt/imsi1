import bpy,json,hashlib,struct
from pathlib import Path
ROOT=Path("/home/chatgpt-runner/work_handoff/ferrari16_slotC_f50_source_audit_20261108")
output=ROOT/"F50_OriginalPMT_VisibleSeat_Bolster_v43.blend"
receipt_path=ROOT/"F50_VisibleSeat_v43_Receipt.json"
receipt=json.loads(receipt_path.read_text())
assert bpy.data.filepath==str(output)
assert hashlib.sha256(output.read_bytes()).hexdigest()==receipt["output_sha256"]
def sig(obj):
 h=hashlib.sha256()
 h.update(obj.name.encode())
 h.update(struct.pack("<16d",*[float(z) for row in obj.matrix_world for z in row]))
 h.update(struct.pack("<QQ",len(obj.data.vertices),len(obj.data.polygons)))
 for v in obj.data.vertices:h.update(struct.pack("<3d",*map(float,v.co)))
 for f in obj.data.polygons:
  h.update(struct.pack("<I",len(f.vertices)))
  for ix in f.vertices:h.update(struct.pack("<I",ix))
 return h.hexdigest()
objects={o.name:o for o in bpy.data.objects if o.type=="MESH"}
assert len(objects)==42
sigs={k:sig(v) for k,v in objects.items()}
assert sigs==receipt["source_mesh_fingerprints_after"]
assert all(sigs[k]==receipt["source_mesh_fingerprints_before"][k] for k in sigs if k!="PMT_F50_object00_group01_material023_a0")
assert sigs["PMT_F50_object00_group01_material023_a0"]!=receipt["source_mesh_fingerprints_before"]["PMT_F50_object00_group01_material023_a0"]
receipt["independent_reopen"]="PASS_BENDER_4_5_15_SEPARATE_PROCESS"
receipt["independent_reopen_meshes"]=len(objects)
receipt["independent_reopen_output_sha256"]=hashlib.sha256(output.read_bytes()).hexdigest()
receipt_path.write_text(json.dumps(receipt,indent=2),encoding="utf8")
print("F50_VISIBLE_SEAT_FRESH_REOPEN_PASS",len(objects),receipt["independent_reopen_output_sha256"])