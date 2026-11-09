from pathlib import Path
import hashlib, sys
root=Path(__file__).resolve().parent
out=root/"Daytona365_SlotA_OriginalPMT005_InnerDoor_R45.blend"
parts=sorted(root.glob("part*.bin"))
with out.open("wb") as w:
    for p in parts:
        w.write(p.read_bytes())
h=hashlib.sha256(out.read_bytes()).hexdigest()
expected="224131c7adc928d5d6f0377d030d5a350c59b8664c13303a2731d6dfc6e9a722"
print(out, h)
if h!=expected:
    raise SystemExit("SHA256 mismatch")
