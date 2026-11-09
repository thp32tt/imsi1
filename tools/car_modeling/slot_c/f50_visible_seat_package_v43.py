from pathlib import Path
import hashlib,shutil,json,subprocess,sys
root=Path("/home/chatgpt-runner/work_handoff/ferrari16_slotC_f50_source_audit_20261108")
out=root/"F50_OriginalPMT_VisibleSeat_Bolster_v43.blend"
rec=json.loads((root/"F50_VisibleSeat_v43_Receipt.json").read_text())
publish=root/"publish_visible_seat_v43";publish.mkdir(exist_ok=True)
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert h(out)==rec["output_sha256"]
prefix=out.stem
parts=[]
block=262144
with out.open("rb") as f:
 for i,chunk in enumerate(iter(lambda:f.read(block),b""),1):
  p=publish/f"{prefix}.part{i:02d}.bin"
  p.write_bytes(chunk)
  parts.append({"file":p.name,"sha256":h(p),"size":p.stat().st_size,"offset":(i-1)*block})
for name in ["F50_VisibleSeat_v43_Receipt.json","F50_VisibleSeat_v43_BEFORE.png","F50_VisibleSeat_v43_AFTER.png","F50_VisibleSeat_v43_BEFORE_AFTER.png"]:
 shutil.copyfile(root/name,publish/name)
manifest={
 "schema_version":1,"bundle":"f50_visible_seat_v43_source_edit","repository":"thp32tt/imsi1","branch":"main",
 "slot":"C","active_car_id":"f50","component":"visible_seat","status":"COVERED_PARTIAL_QA",
 "format":"plain_unencrypted_binary_parts","binary_file":out.name,
 "binary_sha256":h(out),"binary_size":out.stat().st_size,"chunk_size":block,
 "parts":parts,
 "input_baseline":{"file":"F50_OriginalPMT_InnerDoor_UpperRail_v40.blend","sha256":rec["input_sha256"]},
 "original_native_game_resource":{"retained_on_n100":True,"file":"obj_plcar_f50_pmt.sz","sha256":rec["native_original_pmt_sha256"]},
 "original_import_blend_sha256":rec["original_import_blend_sha256"],
 "independent_blender_reopen":"PASS",
 "artifacts_sha256":{n:h(publish/n) for n in ["F50_VisibleSeat_v43_Receipt.json","F50_VisibleSeat_v43_BEFORE.png","F50_VisibleSeat_v43_AFTER.png","F50_VisibleSeat_v43_BEFORE_AFTER.png"]},
 "verification":"python3 reassemble.py --verify-only (or python3 reassemble.py --output /path/file.blend)",
 "unmodified_protected_regions":["windshield","windshield_frame","A_pillars","glass_borders","dashboard","steering_wheel","exterior"],
 "vehicle_qa_pass":False,"next_component":"instrument_cluster"
}
(publish/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
reassemble='''#!/usr/bin/env python3
"""Reassemble plain, unencrypted original-PMT-derived editable .blend parts. SHA256 fail closed."""
from pathlib import Path
import argparse,hashlib,json,sys
def sha(data):return hashlib.sha256(data).hexdigest()
def run():
 ap=argparse.ArgumentParser()
 ap.add_argument("--manifest",type=Path,default=Path(__file__).with_name("manifest.json"))
 ap.add_argument("--output",type=Path,default=None)
 ap.add_argument("--verify-only",action="store_true")
 args=ap.parse_args()
 m=json.loads(args.manifest.read_text(encoding="utf8"))
 root=args.manifest.parent
 chunks=[]
 for x in m["parts"]:
  p=root/x["file"]
  data=p.read_bytes()
  if len(data)!=x["size"] or sha(data)!=x["sha256"]:
   raise SystemExit(f"FAIL part SHA or size: {p}")
  chunks.append(data)
 data=b"".join(chunks)
 if len(data)!=m["binary_size"] or sha(data)!=m["binary_sha256"]:
  raise SystemExit("FAIL reassembled SHA256 or size")
 if not args.verify_only:
  output=args.output or root/m["binary_file"]
  output.write_bytes(data)
  assert sha(output.read_bytes())==m["binary_sha256"]
 print("REASSEMBLE_SHA256_PASS",m["binary_sha256"],len(data))
if __name__=="__main__":run()
'''
(publish/"reassemble.py").write_text(reassemble)
p=subprocess.run([sys.executable,str(publish/"reassemble.py"),"--verify-only"],capture_output=True,text=True)
assert p.returncode==0,(p.stdout,p.stderr)
print("PACKAGING_PASS",p.stdout.strip(),"parts",len(parts))
print(json.dumps({"manifest_sha":h(publish/"manifest.json"),"part_names":[x["file"] for x in parts],"out":str(publish)},indent=2))