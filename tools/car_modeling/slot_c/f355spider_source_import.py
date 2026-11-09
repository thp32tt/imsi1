#!/usr/bin/env python3
"""One-shot F355 Spider original OutRun 2006 .sz PMT -> editable Blender baseline.

SOURCE-ONLY. Imports every native GPU triangle faithfully into Blender; no
modelling, synthetic meshes, added triangles, changed coordinates, textures,
camera, game export, or original game resource writes. Independent fresh reopen.
"""
import hashlib
import json
import os
import struct
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path("/home/chatgpt-runner/worktrees/imsi1-slotC-f355sp-source-20261110")
HERE = Path(__file__).resolve().parent
SOURCE = Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f355sp_pmt.sz")
SOURCE_SHA = "d9af341653ef44371e8df2efc4024af92d7ca03665acef04a4c3c65200bb7b11"
BLENDER = Path("/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender")
OUT = ROOT / "artifacts/slot_C/f355spider/source_bootstrap"
BASE = OUT / "F355Spider_OriginalPMT_SourceBaseline_v1.blend"
EVIDENCE = OUT / "source_import_verification.json"
QUEUE = ROOT / "docs/automation/FERRARI16_GEOMETRY_QUEUE.json"
WORKPACK = ROOT / "docs/automation/FERRARI_COCKPIT_WORKPACK_C_F355SPIDER.json"
sys.path.insert(0, str(HERE))
from f355spider_native_pmt_reader import open_pmt, decode_object

def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def admission():
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    w = json.loads(WORKPACK.read_text(encoding="utf-8"))
    assert q["repository"] == "thp32tt/imsi1" and q["branch"] == "main"
    assert q["active_by_slot"]["C"] == "f355spider"
    assert w["slot"] == "C" and w["car_id"] == "f355spider"
    assert w["input_stage"] == "SOURCE_IMPORT_PENDING"
    assert w["current_component"] == "source_bootstrap"
    assert w["source_bootstrap"]["allowed_bootstrap_attempts"] == 1
    assert w["original_game_resource_file"] == str(SOURCE)
    assert w["original_game_resource_sha256"] == SOURCE_SHA
    assert w["original_import_blend_sha256"] is None and w["migration_input_blend_sha256"] is None
    assert sha_file(SOURCE) == SOURCE_SHA, "original PMT SHA changed"
    return q,w

def part_name(p):
    return "PMT_F355SPIDER_" + p["name"]

def parts_from_original():
    asset = open_pmt(SOURCE)
    assert asset["obj_count"] == 30, "PMT object count changed"
    result = []
    for oi in range(asset["obj_count"]):
        parts = decode_object(asset, oi)
        for p in parts:
            assert p["object"] == oi
            assert len(p["indices"]) % 3 == 0
            assert len(p["vertices"]) == len(p["uvs"]) == len(p["normals"])
            assert len(p["indices"]) > 0 and len(p["vertices"]) > 0
            result.append(p)
    assert len(result) == 96, "native part inventory changed"
    assert len({part_name(p) for p in result}) == len(result)
    return result

def fingerprint(name, coords, norms, uvs, faces):
    h = hashlib.sha256()
    h.update(b"F355SPIDER_NATIVE_MESH_V1\0")
    h.update(name.encode("utf-8"))
    h.update(struct.pack("<II", len(coords), len(faces)))
    assert len(coords) == len(norms) == len(uvs)
    for v, n, uv in zip(coords, norms, uvs):
        h.update(struct.pack("<3f", *[float(t) for t in v]))
        h.update(struct.pack("<3f", *[float(t) for t in n]))
        h.update(struct.pack("<2f", *[float(t) for t in uv]))
    for face in faces:
        assert len(face) == 3
        h.update(struct.pack("<3I", *[int(t) for t in face]))
    return h.hexdigest()

def source_sig(p):
    ids = p["indices"]
    faces = [ids[k:k+3] for k in range(0, len(ids), 3)]
    return fingerprint(part_name(p), p["vertices"], p["normals"], p["uvs"], faces)

def blender_sig(o):
    mesh = o.data
    assert o.type == "MESH"
    assert len(o.constraints) == 0 and o.parent is None
    assert tuple(o.location) == (0.0,0.0,0.0) and tuple(o.rotation_euler) == (0.0,0.0,0.0)
    assert tuple(o.scale) == (1.0,1.0,1.0)
    assert len(mesh.uv_layers) == 1 and mesh.uv_layers[0].name == "PMT_NATIVE_UV0"
    a = mesh.attributes.get("PMT_NATIVE_NORMAL")
    assert a is not None and a.domain == "POINT" and a.data_type == "FLOAT_VECTOR"
    coords = [tuple(v.co) for v in mesh.vertices]
    norms = [tuple(x.vector) for x in a.data]
    uvs = [None] * len(coords)
    triangles = []
    for poly in mesh.polygons:
        assert len(poly.vertices) == 3
        triangles.append(list(poly.vertices))
        for li in poly.loop_indices:
            vi = mesh.loops[li].vertex_index
            uv = tuple(mesh.uv_layers[0].data[li].uv)
            if uvs[vi] is None:
                uvs[vi] = uv
            else:
                assert tuple(struct.pack("<2f", *uv)) == tuple(struct.pack("<2f", *uvs[vi]))
    assert all(uv is not None for uv in uvs)
    return fingerprint(o.name, coords, norms, uvs, triangles)

def import_baseline():
    import bpy
    admission()
    assert not BASE.exists() and not EVIDENCE.exists(), "one-shot output exists; never retry or overwrite"
    assert bpy.app.version[:2] == (4, 5), bpy.app.version_string
    raw = SOURCE.read_bytes()
    native_parts = parts_from_original()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    coll = bpy.data.collections.new("SOURCE_F355SPIDER_ORIGINAL_PMT_UNEDITED")
    sc.collection.children.link(coll)
    sc["source_model"] = "Ferrari F355 Spider"
    sc["source_game_resource_sha256"] = SOURCE_SHA
    sc["source_pmt_uncompressed_sha256"] = hashlib.sha256(zlib.decompress(raw)).hexdigest()
    sc["source_pmt_resource_file"] = SOURCE.name
    sc["coordinate_space"] = "native PMT object-local coordinates; no invented vehicle transforms"
    sc["geometry_edit_count"] = 0
    sc["original_resource_read_only"] = True
    sc["glass_and_glass_adjacent_geometry_untouched"] = True
    sc["whole_vehicle_qa_pass"] = False
    source_fps = {}
    inventory = []
    for p in native_parts:
        name = part_name(p)
        faces = [p["indices"][k:k+3] for k in range(0, len(p["indices"]), 3)]
        mesh = bpy.data.meshes.new(name+"_native_source")
        mesh.from_pydata(p["vertices"], [], faces)
        mesh.update(calc_edges=True)
        uv_layer = mesh.uv_layers.new(name="PMT_NATIVE_UV0")
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                vi = mesh.loops[li].vertex_index
                uv_layer.data[li].uv = p["uvs"][vi]
        normal_attr = mesh.attributes.new(name="PMT_NATIVE_NORMAL", type="FLOAT_VECTOR", domain="POINT")
        for i,normal in enumerate(p["normals"]):
            normal_attr.data[i].vector = normal
        ob = bpy.data.objects.new(name,mesh)
        coll.objects.link(ob)
        ob["original_pmt_object_id"] = p["name"]
        ob["original_pmt_object_index"] = p["object"]
        ob["original_pmt_group_index"] = p["group"]
        ob["original_pmt_material_group"] = p["material_group"]
        ob["original_pmt_alpha_group"] = p["alpha"]
        ob["original_pmt_texture_id"] = p["tex_index"] if p["tex_index"] is not None else -1
        ob["source_pmt_sha256"] = SOURCE_SHA
        ob["native_unmodified"] = True
        expected = source_sig(p)
        actual = blender_sig(ob)
        assert expected == actual, (name,expected,actual)
        source_fps[name] = expected
        inventory.append({"name":name,"original_id":p["name"],"object_index":p["object"],
            "group_index":p["group"],"material_group":p["material_group"],
            "vertex_count":len(p["vertices"]),"triangle_count":len(faces),
            "texture_index":p["tex_index"],"sha256":expected})
    assert len(bpy.data.objects) == 96 and all(o.type == "MESH" for o in bpy.data.objects)
    OUT.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BASE),compress=True)
    assert BASE.is_file() and BASE.stat().st_size > 100000
    assert sha_file(SOURCE) == SOURCE_SHA
    # Receipt is created only by the distinct Blender reopen process.
    print("SOURCE_IMPORT_SAVED",sha_file(BASE),"PARTS",len(inventory),flush=True)

def verify_independent_reopen():
    import bpy
    admission()
    assert bpy.app.version[:2] == (4,5), bpy.app.version_string
    assert BASE.is_file() and not EVIDENCE.exists()
    assert Path(bpy.data.filepath).resolve() == BASE.resolve(), "not a freshly reopened source .blend"
    native_parts = parts_from_original()
    native = {part_name(p):p for p in native_parts}
    objects = {o.name:o for o in bpy.data.objects}
    assert len(objects) == len(native) == 96
    assert objects.keys() == native.keys(), "mesh object IDs do not match original import"
    fingerprints = {}
    counts = {"vertices":0,"triangles":0}
    inventory = []
    for name,p in native.items():
        ob = objects[name]
        assert ob["original_pmt_object_id"] == p["name"]
        assert ob["original_pmt_object_index"] == p["object"]
        assert ob["source_pmt_sha256"] == SOURCE_SHA
        assert ob["native_unmodified"] is True
        expected = source_sig(p)
        actual = blender_sig(ob)
        assert expected == actual, ("independent reopen mismatch",name,expected,actual)
        fingerprints[name] = actual
        nv = len(p["vertices"])
        nf = len(p["indices"])//3
        counts["vertices"] += nv
        counts["triangles"] += nf
        inventory.append({"name":name,"original_id":p["name"],"object_index":p["object"],
                          "vertices":nv,"triangles":nf,"fingerprint":actual})
    assert bpy.context.scene["geometry_edit_count"] == 0
    assert bpy.context.scene["glass_and_glass_adjacent_geometry_untouched"] is True
    assert bpy.context.scene["source_game_resource_sha256"] == SOURCE_SHA
    assert sha_file(SOURCE) == SOURCE_SHA
    blend_sha = sha_file(BASE)
    receipt = {
        "schema_version":1,
        "status":"SOURCE_VERIFIED",
        "slot":"C",
        "vehicle":"f355spider",
        "github_initial_head":"8af6cac75a21808b9ecafa919f285428468a4153",
        "source_file_name":SOURCE.name,
        "original_game_resource_sha256":SOURCE_SHA,
        "source_file_size_bytes":SOURCE.stat().st_size,
        "uncompressed_pmt_sha256":bpy.context.scene["source_pmt_uncompressed_sha256"],
        "source_decoder":"tools/car_modeling/slot_c/f355spider_native_pmt_reader.py",
        "import_script":"tools/car_modeling/slot_c/f355spider_source_import.py",
        "blender_version":bpy.app.version_string,
        "import_blend":"artifacts/slot_C/f355spider/source_bootstrap/"+BASE.name,
        "original_import_blend_sha256":blend_sha,
        "migration_input_blend_sha256":blend_sha,
        "independent_blender_reopen":"PASS_SEPARATE_BLENDER_PROCESS",
        "native_object_count":len(inventory),
        "native_pmt_object_count":30,
        "native_totals":counts,
        "original_mesh_object_ids":[x["name"] for x in inventory],
        "native_mesh_fingerprints":fingerprints,
        "original_mesh_inventory":inventory,
        "coordinate_policy":"original PMT object-local coordinates without transforms",
        "geometry_edit_count":0,
        "windshield_and_glass_adjacent_meshes_untouched":True,
        "original_game_resource_modified":False,
        "new_vehicle_or_synthetic_mesh":False,
        "photos_or_pmt_published":False,
        "game_export":False,
        "full_vehicle_qa_pass":False,
        "next_component":"center_console",
        "topology_note":"Faithful native indexed GPU primitives reconstructed as Blender triangles; no arbitrary reshaping"
    }
    EVIDENCE.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    assert sha_file(BASE)==blend_sha
    print("SOURCE_VERIFIED_F355SPIDER",blend_sha,"MESHES",len(fingerprints),"COUNTS",json.dumps(counts),flush=True)

def driver():
    admission()
    assert BLENDER.is_file(), "official blender unavailable"
    assert not BASE.exists() and not EVIDENCE.exists(), "one-shot import already attempted"
    cmds=[
        [str(BLENDER),"--background","-noaudio","-t","2","--factory-startup","--python",str(HERE/"f355spider_source_import.py"),"--","import"],
        [str(BLENDER),"--background","-noaudio","-t","2",str(BASE),"--python",str(HERE/"f355spider_source_import.py"),"--","reopen"],
    ]
    for step,cmd in zip(("SOURCE_IMPORT","INDEPENDENT_REOPEN"),cmds):
        p=subprocess.run(cmd,cwd=str(ROOT),text=True,capture_output=True,timeout=180)
        print(step,"EXIT",p.returncode,"STDOUT",p.stdout[-11000:],"STDERR",p.stderr[-4500:],flush=True)
        if p.returncode:
            raise SystemExit(step+"_FAILED_NO_RETRY")
    rec=json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert rec["status"]=="SOURCE_VERIFIED" and sha_file(BASE)==rec["original_import_blend_sha256"]
    print("F355SPIDER_ONE_SHOT_SOURCE_BASELINE_PASS",rec["original_import_blend_sha256"],flush=True)

if __name__=="__main__":
    if "--" in sys.argv:
        mode = sys.argv[sys.argv.index("--")+1]
    else:
        mode = sys.argv[1] if len(sys.argv)==2 else ""
    if mode=="import":
        import_baseline()
    elif mode=="reopen":
        verify_independent_reopen()
    elif mode=="run":
        driver()
    else:
        raise SystemExit("specify run/import/reopen")