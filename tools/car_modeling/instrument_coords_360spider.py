#!/usr/bin/env python3
import bpy,json,collections
from pathlib import Path
R=Path(__file__).resolve().parents[2];D=R/"artifacts/slot_A/360spider/instrument_cluster_20261110"
bpy.ops.wm.open_mainfile(filepath=str(R/"artifacts/slot_A/360spider/visible_seat_20261110/Ferrari360Spider_VisibleSeat_OriginalPMT_R02.blend"))
m=bpy.data.objects["PMT_object00_group01_material010_a0"].data
data=json.loads((D/"native_islands.json").read_text())
ids=[a for a in data if a["object"]=="PMT_object00_group01_material010_a0" and a["index_min"] in (1594,1580,1617,1565,1628)]
for a in ids:
 print("ISLAND",a["index_min"],a["n"],flush=True)
 for idx in a["vertex_indices"]:
  p=m.vertices[idx].co
  print(idx,*[round(float(v),5) for v in p],flush=True)
