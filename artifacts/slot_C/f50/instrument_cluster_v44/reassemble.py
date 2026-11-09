#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--output",type=Path)
p.add_argument("--verify-only",action="store_true")
a=p.parse_args()
root=Path(__file__).resolve().parent
m=json.loads((root/"manifest.json").read_text())
data=bytearray()
for part in m["parts"]:
    raw=(root/part["file"]).read_bytes()
    assert len(raw)==part["size"] and hashlib.sha256(raw).hexdigest()==part["sha256"]
    assert len(data)==part["offset"]
    data.extend(raw)
assert len(data)==m["binary_size"]
assert hashlib.sha256(data).hexdigest()==m["binary_sha256"]
if a.output and not a.verify_only:
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(data)
    assert hashlib.sha256(a.output.read_bytes()).hexdigest()==m["binary_sha256"]
print("PLAINTEXT_REASSEMBLE_SHA256_PASS",m["binary_sha256"])