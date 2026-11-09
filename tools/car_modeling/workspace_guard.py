#!/usr/bin/env python3
"""Fail-closed, stdlib-only Ferrari A/C dispatch and native-mesh receipt guard.

No Blender or original game asset is required for preflight. This tool NEVER
modifies a queue, workpack, receipt or .blend. Run preflight BEFORE Blender edits
and receipt verification AFTER an independent Blender reopen.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{64}$")
PROTECTED = re.compile(
    r"windshield|windscreen|front[_ -]?glass|glass[_ -]?border|glass[_ -]?seal|"
    r"a[_ -]?pillar|front[_ -]?window|wind[_ -]?screen",
    re.IGNORECASE,
)
HOLD = {"dashboard", "steering_wheel"}
EDITABLE = {"NOT_STARTED", "IN_PROGRESS"}


class GuardError(ValueError):
    pass


def require(condition, msg):
    if not condition:
        raise GuardError(msg)


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise GuardError(f"unreadable JSON {path}: {exc}") from exc


def valid_sha(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def check_identity(queue, workpack, slot, require_baseline=True):
    require(slot in ("A", "C"), "only existing slot A or C is authorized")
    require(queue.get("repository") == "thp32tt/imsi1" and queue.get("branch") == "main",
            "queue SSOT must be imsi1@main")
    active = queue.get("active_by_slot", {})
    require(set(active) == {"A", "C"} and active.get("A") != active.get("C"),
            "missing or overlapping A/C active vehicles")
    require(active.get(slot) == workpack.get("car_id") and workpack.get("slot") == slot,
            "slot/workpack vehicle mismatch; refuse cross-car edit")
    strategy = queue.get("strategy_v3", {})
    expected = strategy.get("component_sequence")
    actual = workpack.get("component_order")
    require(isinstance(expected, list) and expected and expected == actual,
            "component ordering differs from queue SSOT")
    require(not any(PROTECTED.search(str(x)) for x in expected),
            "windshield/glass region must not be schedulable")
    require(strategy.get("protected_regions", {}).get("windshield_and_front_glass") == "DO_NOT_EDIT",
            "windshield protection missing from queue")
    require(workpack.get("max_dispatches_per_component") == strategy.get("dispatch_turn_limit_per_component") == 2,
            "two-dispatch budget must not be changed")
    require(valid_sha(workpack.get("original_game_resource_sha256")),
            "authentic original game PMT SHA256 required")
    if require_baseline:
        require(all(valid_sha(workpack.get(k)) for k in (
            "original_import_blend_sha256", "migration_input_blend_sha256")),
                "native Blender import/accepted migration SHA256 required before geometry")
        require(workpack.get("input_stage") not in {"SOURCE_IMPORT_PENDING", "SOURCE_IMPORT_BLOCKED"},
                "native original import not yet independently verified")
    else:
        require(workpack.get("input_stage") == "SOURCE_IMPORT_PENDING",
                "bootstrap only for unresolved original game import")
        require(not workpack.get("original_import_blend_sha256") and
                not workpack.get("migration_input_blend_sha256"),
                "bootstrap may not overwrite an existing Blender import")
    require(isinstance(workpack.get("components"), dict), "component records absent")
    for name in expected:
        require(name in workpack["components"], f"component record missing: {name}")
        item = workpack["components"][name]
        require(type(item.get("source_edits_this_phase", 0)) is int and
                0 <= item.get("source_edits_this_phase", 0) <= 2,
                f"edit cap exceeded or invalid: {name}")
        for field in ("dispatches_used", "dispatches_consumed_this_phase"):
            if field in item:
                require(type(item[field]) is int and 0 <= item[field] <= 2,
                        f"dispatch cap exceeded or invalid: {name}.{field}")
        if item.get("status") == "COVERED_PARTIAL_QA":
            require(item.get("source_edits_this_phase", 0) >= 1,
                    f"partial coverage without native edit: {name}")
    for name, item in workpack["components"].items():
        if PROTECTED.search(name):
            # Historical reverted edits are recorded, never implicitly accepted.
            require(item.get("status", "").startswith("PROTECTED"),
                    "protected component must remain excluded")
    return expected


def preflight(queue, workpack, slot, component=None):
    sequence = check_identity(queue, workpack, slot)
    current = workpack.get("current_component")
    target = component or current
    require(target in sequence and not PROTECTED.search(str(target)),
            "requested component is outside authorized original cockpit sequence")
    require(target == current, "requested region differs from persisted current_component")
    require(workpack.get("components", {}).get(target, {}).get("status") in EDITABLE,
            "target already finished, blocked or on P0 hold; advance instead")
    turns = workpack.get("dispatches_on_component")
    require(type(turns) is int and 0 <= turns < 2,
            "two-dispatch limit reached; move to next component")
    item = workpack["components"][target]
    for field in ("dispatches_used", "dispatches_consumed_this_phase"):
        if field in item:
            require(item[field] < 2, "stored component dispatch budget exhausted")
    require(item.get("source_edits_this_phase", 0) < 2,
            "two material-edit limit reached")
    if target in HOLD:
        prior = sequence[:sequence.index(target)]
        require(all(workpack["components"][p].get("status") in {"COVERED_PARTIAL_QA", "OUT_OF_VIEW", "BLOCKED"} for p in prior),
                "P0 initial pass requires documented earlier cockpit coverage or source blockers")
        require(item.get("source_edits_this_phase", 0) == 0 and item.get("status") == "NOT_STARTED",
                "P0 historical polish retry requires an explicit new user defect ID")
        # Fresh vehicles get one initial source-backed dashboard/wheel pass; the old
        # 40+ iteration P0 loop remains permanently barred without user approval.
    require(target != "cross_cockpit_qa", "cross-cockpit QA is observation-only, not mesh edit")
    return f"PASS {slot}/{workpack['car_id']} target={target} turn={turns + 1}/2"


def verify_receipt(queue, workpack, slot, receipt, output_blend=None):
    check_identity(queue, workpack, slot)
    require(receipt.get("slot") == slot and receipt.get("vehicle") == workpack["car_id"],
            "receipt crossed slot/vehicle")
    part = receipt.get("component")
    require(part in workpack["component_order"] and part not in HOLD and not PROTECTED.search(str(part)),
            "receipt contains protected/non-editable region")
    require(receipt.get("status") == "COVERED_PARTIAL_QA" and receipt.get("full_vehicle_qa_pass") is False,
            "interim source edit cannot claim vehicle QA PASS")
    require(receipt.get("native_original_pmt_sha256") == workpack["original_game_resource_sha256"],
            "original game asset SHA mismatch")
    require(receipt.get("original_import_blend_sha256") == workpack["original_import_blend_sha256"],
            "original imported Blender SHA mismatch")
    for field in ("input_sha256", "output_sha256"):
        require(valid_sha(receipt.get(field)), f"invalid {field}")
    require(receipt["input_sha256"] != receipt["output_sha256"],
            "no source checkpoint change")
    require(str(receipt.get("input_blend", "")).endswith(".blend") and
            str(receipt.get("output_blend", "")).endswith(".blend"), "source/output must be editable .blend")
    require(receipt.get("blender_saved") is True and str(receipt.get("independent_reopen", "")).startswith("PASS"),
            "real save and independent fresh Blender reopen required")
    before = receipt.get("source_mesh_fingerprints_before")
    after = receipt.get("source_mesh_fingerprints_after")
    modified = receipt.get("modified_objects")
    require(isinstance(before, dict) and isinstance(after, dict) and len(before) >= 2 and
            before.keys() == after.keys(), "native mesh inventory was removed/added")
    require(all(valid_sha(v) for v in list(before.values()) + list(after.values())),
            "missing native geometry fingerprints")
    require(isinstance(modified, list) and modified and len(set(modified)) == len(modified),
            "no unique modified original mesh list")
    require(all(isinstance(n, str) and n.startswith("PMT_") and not PROTECTED.search(n)
                for n in modified), "non-original or visibly protected Blender object")
    changed = sorted(k for k in before if before[k] != after[k])
    require(changed == sorted(modified),
            "unapproved mesh changed, or purported target had no actual geometry delta")
    require(receipt.get("original_mesh") in modified,
            "native source object not among changed meshes")
    require(receipt.get("unchanged_other_native_meshes") == len(before) - len(modified),
            "non-target unchanged native mesh count mismatch")
    require(receipt.get("windshield_and_other_regions_untouched") is True,
            "windshield/non-target isolation has not been attested")
    if part == "visible_seat":
        require(receipt.get("nonseat_components_within_target_unchanged") is True,
                "seat mesh includes non-seat geometry without internal isolation proof")
    require(type(receipt.get("changed_existing_vertices")) is int and receipt["changed_existing_vertices"] > 0,
            "no proven existing original vertices modified")
    require(receipt.get("exports") == [] and receipt.get("new_textures") == [],
            "unapproved exports or generated materials")
    if output_blend is not None:
        path = Path(output_blend)
        require(path.is_file() and path.name == receipt["output_blend"], "output file missing/renamed")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == receipt["output_sha256"],
                "actual output .blend SHA mismatch")
    return f"PASS {slot}/{workpack['car_id']} receipt={part} changed_native_objects={len(modified)}"


def bootstrap_preflight(queue, workpack, slot, original_resource):
    """Source-only bootstrap admission: no mesh edit and no fake import SHA."""
    check_identity(queue, workpack, slot, require_baseline=False)
    require(workpack.get("current_component") == "source_bootstrap" and
            workpack.get("dispatches_on_component") == 0,
            "source bootstrap must precede first cockpit geometry dispatch")
    expected = Path(workpack.get("original_game_resource_file", ""))
    actual = Path(original_resource)
    require(expected == actual and str(actual).startswith(
            "/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/") and
            actual.name.startswith("obj_plcar_") and actual.name.endswith("_pmt.sz"),
            "source-only bootstrap must use protected N100 game PMT pathname")
    require(actual.is_file() and hashlib.sha256(actual.read_bytes()).hexdigest() ==
            workpack["original_game_resource_sha256"],
            "original game PMT missing or SHA256 mismatched")
    return f"PASS SOURCE_BOOTSTRAP {slot}/{workpack['car_id']} pmt_sha256={workpack['original_game_resource_sha256']}"


def paths(root, slot):
    """Resolve the current car from queue, not hardwired Daytona/F50 filenames."""
    queue_path = root / "docs/automation/FERRARI16_GEOMETRY_QUEUE.json"
    queue = read_json(queue_path)
    car_id = (queue.get("active_by_slot") or {}).get(slot)
    record = next((car for car in queue.get("cars", [])
                   if car.get("id") == car_id and car.get("slot") == slot), None)
    rel = record.get("workpack_path") if record else None
    require(isinstance(rel, str) and rel.startswith("docs/automation/FERRARI_COCKPIT_WORKPACK_")
            and rel.endswith(".json") and ".." not in rel and "/" not in
            rel[len("docs/automation/"):],
            "current Ferrari slot lacks safe GitHub workpack path")
    return queue_path, root / rel


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["audit-workspace", "preflight", "verify-receipt", "bootstrap-source"])
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--slot", choices=["A", "C"])
    parser.add_argument("--component")
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--output-blend", type=Path)
    parser.add_argument("--original-resource", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == "audit-workspace":
            for slot in ("A", "C"):
                q, w = paths(args.root, slot)
                queue, pack = read_json(q), read_json(w)
                check_identity(queue, pack, slot)
                print(f"PASS {slot} governance: {pack['car_id']} current={pack['current_component']}")
            return 0
        require(args.slot is not None, "--slot is mandatory")
        q, w = paths(args.root, args.slot)
        queue, pack = read_json(q), read_json(w)
        if args.action == "preflight":
            print(preflight(queue, pack, args.slot, args.component))
        elif args.action == "bootstrap-source":
            require(args.original_resource is not None, "--original-resource required for bootstrap")
            print(bootstrap_preflight(queue, pack, args.slot, args.original_resource))
        else:
            require(args.receipt is not None, "--receipt is mandatory")
            print(verify_receipt(queue, pack, args.slot, read_json(args.receipt), args.output_blend))
        return 0
    except GuardError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
