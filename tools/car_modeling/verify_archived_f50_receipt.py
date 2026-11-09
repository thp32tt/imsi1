#!/usr/bin/env python3
"""Historical F50 native seat receipt audit, independent of current slot C owner.

No data is changed; archived F50 checks cannot be used to claim active-car QA PASS.
"""
from pathlib import Path
from workspace_guard import read_json, verify_receipt

root=Path(__file__).resolve().parents[2]
queue=read_json(root/"docs/automation/FERRARI16_GEOMETRY_QUEUE.json")
f50=next((c for c in queue.get("cars",[]) if c.get("id")=="f50"),None)
if not f50 or f50.get("status") not in {"ACTIVE","QA_PARKED"}:
    raise SystemExit("BLOCKED: missing archived F50 provenance")
workpack_path=f50.get("workpack_path")
if workpack_path!="docs/automation/FERRARI_COCKPIT_WORKPACK_C_F50.json":
    raise SystemExit("BLOCKED: unexpected archived workpack")
workpack=read_json(root/workpack_path)
receipt=read_json(root/"artifacts/slot_C/f50/visible_seat_v43/F50_VisibleSeat_v43_Receipt.json")
# Snapshot-only historical admission: DO NOT edit actual active_by_slot or workpack.
historical_queue={**queue,"active_by_slot":{**queue["active_by_slot"],"C":"f50"}}
result=verify_receipt(historical_queue,workpack,"C",receipt)
print(result+" ARCHIVED_RECEIPT_ONLY_NOT_VEHICLE_QA")
