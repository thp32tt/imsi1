#!/usr/bin/env python3
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