# Ferrari F50 — SLOT C visible_seat repeated dispatch guard (2026-11-09)

**Result:** `BLOCKED_OUT_OF_ORDER` (new geometry **not performed**).

Latest SSOT examined: `thp32tt/imsi1@92bcb9c3d3a7238f28093caca34d7a91d470b76a`. `active_by_slot.C=f50`, `workpack.current_component=instrument_cluster`. The requested `visible_seat` was already covered as `COVERED_PARTIAL_QA` in original PMT023 v43 and moved on. Mandatory source guard was run from latest `tools/car_modeling/workspace_guard.py` with `preflight --slot C --component visible_seat`, using the matching queue/workpack snapshot, and returned:

```text
BLOCKED: requested region differs from persisted current_component
```

This is an authorized stop, **not** absence of AES/Secret/decryption, not a missing original PMT, not a failed Blender render, and not a whole-car QA pass. The second same-region instruction consumes the remaining seat dispatch slot: `dispatches_used=2/2`, `source_edits_this_phase=1`; no second material edit, no new `.blend`, no synthetic model, no changed source bytes, no new textures/PBR or export, no score.

Accepted prior v43 `.blend` SHA256: `a1f64d8f2f7e540978cfb9ae41c58dde2732f6a83c0a537c8860dee09f3768c7`; original F50 PMT SHA256: `10daa1312b6cff0267b38b4c440c6007c68b470a225ca15f0c324876fd80aeab`. Existing plaintext partNN/manifest and independent Blender reopen proof remain `artifacts/slot_C/f50/visible_seat_v43/`; nothing is reuploaded, rescored, or regenerated.

**Next/current component:** `instrument_cluster` (0/2); do not silently edit a different component while handling a visible_seat-targeted request. F50 retains 24-hour vehicle assignment; whole-car QA remains **NOT PASS**. All dashboard/wheel, front windshield, A-pillars/glass and other car slots unmodified.
