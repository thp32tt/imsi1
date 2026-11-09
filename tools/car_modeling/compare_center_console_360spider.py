#!/usr/bin/env python3
"""Compare verified native-only Ferrari 360 console Blender before/after QA frames."""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
import json,hashlib
D=Path("/home/chatgpt-runner/imsi1_slotA_360sp_console_20261110/artifacts/slot_A/360spider/center_console_20261110")
all_stats={}
for axis in ("top","oblique"):
 a=Image.open(D/f"before_{axis}.png").convert("RGB")
 b=Image.open(D/f"after_{axis}.png").convert("RGB")
 assert a.size==b.size==(1000,660)
 aa=a.tobytes();bb=b.tobytes()
 changed=0;max_delta=0
 for i in range(0,len(aa),3):
  ds=[abs(aa[i+k]-bb[i+k]) for k in range(3)]
  if max(ds)>3:changed+=1
  max_delta=max(max_delta,max(ds))
 canvas=Image.new("RGB",(2000,700),(246,247,248))
 canvas.paste(a,(0,40));canvas.paste(b,(1000,40))
 d=ImageDraw.Draw(canvas)
 d.text((24,12),f"Ferrari 360 Spider — original {axis} — BEFORE",fill=(15,15,15))
 d.text((1024,12),f"Ferrari 360 Spider — source edit R01 {axis} — AFTER",fill=(15,15,15))
 p=D/f"comparison_{axis}.png";canvas.save(p,optimize=True)
 all_stats[axis]={"changed_RGB_pixels_gt3":changed,"max_channel_delta":max_delta,
  "total_pixels":1000*660,"comparison_sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
(D/"visual_diff_metrics.json").write_text(json.dumps(all_stats,indent=2)+"\n")
print(json.dumps(all_stats,indent=2))
