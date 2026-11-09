#!/usr/bin/env python3
"""One-shot, read-only original-PMT cockpit checkpoint audit for SLOT A 360 Spider."""
import hashlib, json, os, subprocess, sys
from pathlib import Path

REPO = Path("/home/chatgpt-runner/imsi1_slotA_steering_20261110")
BASE = REPO / "artifacts/slot_A/360spider"
BLENDER = "/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender"
STAGES = [
    ("R00", "source_bootstrap/Ferrari360Spider_OriginalPMT_EditableBaseline.blend", "b4f1d071119693172bbf786809da62dce8acb0c84e52d9779a6b1a996654ce57", 0),
    ("R01", "center_console_20261110/Ferrari360Spider_CenterConsole_SourceEdit_R01.blend", "5dabffb52ae4136b6b72f99c7975b629820f839afec2048e59035cb74d8ee612", 16),
    ("R02", "visible_seat_20261110/Ferrari360Spider_VisibleSeat_OriginalPMT_R02.blend", "af5a9a9d9650d261b1b24f56e5ff8b5291773e033c43087e000276940fbc87a2", 20),
    ("R03", "instrument_cluster_20261110/Ferrari360Spider_InstrumentCluster_OriginalPMT_R03.blend", "df7b2ce23530c4bdace9d301cde61526d5ef5ab80ab7f9811f35d4dda08de443", 20),
    ("R04", "dashboard_20261110/Ferrari360Spider_Dashboard_OriginalPMT_R04.blend", "403ec48d0e9761214f20a5c22a7df608f38b3644b135b80aa185dcb559c33ad8", 6),
]
SOURCE = Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_360sp_pmt.sz")
SOURCE_SHA = "a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6"
TARGET_MESH = "PMT_object00_group01_material010_a0"
OUT_DIR = BASE / "cross_cockpit_qa_20261110"

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

if "--inside-blender" not in sys.argv:
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "2"
    proc = subprocess.run(
        [BLENDER, "-b", "-t", "2", "--factory-startup", "--python", str(Path(__file__).resolve()), "--", "--inside-blender"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, timeout=110,
    )
    print("RETURN_CODE:", proc.returncode)
    print("BLENDER_STDOUT:", proc.stdout[-9000:])
    print("BLENDER_STDERR:", proc.stderr[-1600:])
    sys.exit(proc.returncode)

import bpy

def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    snap = {}
    for obj in bpy.data.objects:
        if obj.type != "MESH" or not obj.name.startswith("PMT_"):
            continue
        mesh = obj.data
        snap[obj.name] = {
            "vertices": [tuple(float(v) for v in x.co) for x in mesh.vertices],
            "faces": [tuple(int(v) for v in p.vertices) for p in mesh.polygons],
            "matrix": [round(float(x), 9) for row in obj.matrix_world for x in row],
            "edges": [tuple(int(v) for v in edge.vertices) for edge in mesh.edges],
        }
    return snap

assert SOURCE.is_file() and sha256(SOURCE) == SOURCE_SHA, "Original PMT SHA mismatch"
snaps = {}
file_hashes = {"original_game_resource": {"path_on_N100_only": str(SOURCE), "sha256": SOURCE_SHA}}
for stage, rel, expected_sha, expected_diff in STAGES:
    path = BASE / rel
    actual_sha = sha256(path)
    assert actual_sha == expected_sha, f"{stage}: file sha mismatch"
    file_hashes[stage] = {"repo_path": str(path.relative_to(REPO)), "sha256": actual_sha, "bytes": path.stat().st_size}
    snaps[stage] = snapshot(path)
    print("LOADED", stage, "meshes", len(snaps[stage]), "sha256", actual_sha, flush=True)

original = snaps["R00"]
assert len(original) == 75, f"Expected 75 native PMT meshes; found {len(original)}"
assert sum(len(x["vertices"]) for x in original.values()) == 12424
assert TARGET_MESH in original
proof = []
all_changed_from_original = set()
for i, (stage, rel, expected_sha, expected_changed) in enumerate(STAGES[1:], 1):
    prev = STAGES[i - 1][0]
    curr = snaps[stage]
    before = snaps[prev]
    assert set(curr) == set(original), stage + ": native object IDs changed"
    assert set(before) == set(original), prev + ": native object IDs changed"
    topology_errors = []
    matrix_errors = []
    changed = {}
    for name in sorted(original):
        if curr[name]["faces"] != original[name]["faces"] or curr[name]["edges"] != original[name]["edges"] or len(curr[name]["vertices"]) != len(original[name]["vertices"]):
            topology_errors.append(name)
        if curr[name]["matrix"] != original[name]["matrix"]:
            matrix_errors.append(name)
        delta_indices = []
        for n, (before_v, after_v) in enumerate(zip(before[name]["vertices"], curr[name]["vertices"])):
            if any(abs(a-b) > 1e-7 for a,b in zip(before_v,after_v)):
                delta_indices.append(n)
        if delta_indices:
            changed[name] = delta_indices
    assert not topology_errors, f"{stage} topology changes: {topology_errors}"
    assert not matrix_errors, f"{stage} transform changes: {matrix_errors}"
    assert set(changed) == {TARGET_MESH}, f"{stage} non-target PMT changes: {list(changed)}"
    assert len(changed[TARGET_MESH]) == expected_changed, f"{stage} expected {expected_changed}, got {len(changed[TARGET_MESH])}"
    assert not (set(changed[TARGET_MESH]) & all_changed_from_original), f"{stage} overlaps with earlier edits"
    all_changed_from_original.update(changed[TARGET_MESH])
    proof.append({
        "step": prev+"->"+stage,
        "modified_native_mesh": TARGET_MESH,
        "changed_vertex_count": len(changed[TARGET_MESH]),
        "changed_vertex_indices": changed[TARGET_MESH],
        "untouched_native_mesh_count": 74,
        "native_mesh_ids_identical": True,
        "all_face_edge_topology_invariant": True,
        "all_object_transforms_invariant": True,
        "prior_step_vertex_edits_preserved_and_disjoint": True,
    })
last = snaps["R04"]
cumulative = {i for i,(a,b) in enumerate(zip(original[TARGET_MESH]["vertices"], last[TARGET_MESH]["vertices"])) if any(abs(x-y)>1e-7 for x,y in zip(a,b))}
assert cumulative == all_changed_from_original, f"Cumulative geometry not retained {len(cumulative)} vs {len(all_changed_from_original)}"
for name in original:
    if name != TARGET_MESH:
        assert original[name] == last[name], f"R04 unrelated native mesh changed {name}"
audit = {
    "schema_version": 1, "task_id": "FERRARI16-SLOTA-360SPIDER-CROSS-COCKPIT-QA-20261110",
    "slot": "A", "car_id": "360spider", "component": "cross_cockpit_qa",
    "geometry_integration": "PASS_R00_R01_R02_R03_R04_EXISTING_CHECKPOINTS",
    "original_PMT_sha256": SOURCE_SHA, "input_output_sha256": file_hashes,
    "native_original_meshes": 75, "native_original_vertices": 12424,
    "latest_scene_R04_SHA256": file_hashes["R04"]["sha256"],
    "source_object_IDs_and_topology_invariant": True,
    "non_target_native_meshes_untouched": 74,
    "protected_windshield_frame_glass_unchanged_by_non_target_mesh_audit": True,
    "shared_mesh_only_expected_native_vertex_indices_changed": True,
    "total_unique_cumulative_modified_vertices": len(cumulative),
    "per_component_persisted_changes": proof,
    "camera_calibration": "MISSING_ORIGINAL_GAME_SEATED_DRIVER_EYE",
    "matched_photo_seven_views": "UNVERIFIED_NOT_CALIBRATED",
    "photo_assets": "N100_ONLY_DO_NOT_PUBLISH; 04_360_Spider/REFERENCE_LINKS.md",
    "whole_car_qa": "QA_WAITING_INPUT",
    "full_vehicle_qa_pass": False,
    "new_geometry_created_during_this_audit": False,
    "new_blend_created_during_this_audit": False,
    "dispatches_consumed": 0,
    "score_change": 0,
}
OUT_DIR.mkdir(parents=True, exist_ok=True)
dest = OUT_DIR / "geometry_audit.json"
if dest.exists():
    raise RuntimeError("QA report exists; avoid duplicate same-input audit")
dest.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("AUDIT_PASS", str(dest), "changed", len(cumulative), "steps", [p["changed_vertex_count"] for p in proof], flush=True)