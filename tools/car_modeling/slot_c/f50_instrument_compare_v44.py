#!/usr/bin/env python3
"""Compose two matched native Blender render captures; never publish private F50 photos."""
from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[3]/"artifacts/slot_C/f50/instrument_cluster_v44"
before=root/"F50_InstrumentCluster_v44_BEFORE.png"
after=root/"F50_InstrumentCluster_v44_AFTER.png"
dst=root/"F50_InstrumentCluster_v44_BEFORE_AFTER.png"
with Image.open(before) as a,Image.open(after) as b:
    assert a.size==b.size
    out=Image.new("RGB",(a.width*2,a.height+42),(35,35,35))
    out.paste(a.convert("RGB"),(0,42));out.paste(b.convert("RGB"),(a.width,42))
    draw=ImageDraw.Draw(out)
    draw.text((20,13),"F50 native instrument hood: BEFORE",fill=(250,250,250))
    draw.text((a.width+20,13),"AFTER - 40 original vertices changed",fill=(250,250,250))
    out.save(dst,optimize=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=root/"manifest.json"
m=json.loads(manifest.read_text())
m["artifact_sha256"][dst.name]=sha(dst)
manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf8")
print("F50_COMPARISON_RENDER_PASS",dst.name,sha(dst))