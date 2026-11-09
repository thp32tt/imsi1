#!/usr/bin/env python3
"""F50 SLOT C instrument_cluster v44: change ONLY existing native PMT gauge hood vertices.

The official Blender is invoked on the N100 because original licensed PMT and private
photo references remain there. No synthetic meshes, textures, or game exports.
"""
from pathlib import Path
import hashlib
import json
import math
import subprocess
import struct
import sys

ROOT=Path("/home/chatgpt-runner/worktrees/imsi1-slotC-instrument-20261109-1300")
BASE=Path("/home/chatgpt-runner/work_handoff/ferrari16_slotC_f50_source_audit_20261108/F50_OriginalPMT_VisibleSeat_Bolster_v43.blend")
OUT=ROOT/"artifacts/slot_C/f50/instrument_cluster_v44"
BLENDER="/home/chatgpt-runner/work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender"
TARGET="PMT_F50_object00_group01_material011_a0"
FACE="PMT_F50_object00_group01_material028_a0"
SHA_INPUT="a1f64d8f2f7e540978cfb9ae41c58dde2732f6a83c0a537c8860dee09f3768c7"
SHA_PMT="10daa1312b6cff0267b38b4c440c6007c68b470a225ca15f0c324876fd80aeab"
SHA_IMPORT="d82b3d024a812126da5b38c56572cfc326fbe3d1b5c0ddf8cad4cbd855119d31"
PMT=Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f50_pmt.sz")
OUTPUT=OUT/"F50_OriginalPMT_InstrumentCluster_v44.blend"
RECEIPT=OUT/"receipt.json"

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def sig(obj):
    h=hashlib.sha256()
    h.update(obj.name.encode())
    h.update(struct.pack("<16d",*(float(x) for row in obj.matrix_world for x in row)))
    h.update(struct.pack("<QQ",len(obj.data.vertices),len(obj.data.polygons)))
    for v in obj.data.vertices:
        h.update(struct.pack("<3d",*map(float,v.co)))
    for f in obj.data.polygons:
        h.update(struct.pack("<I",len(f.vertices)))
        for i in f.vertices: h.update(struct.pack("<I",i))
    return h.hexdigest()

def source_inventory():
    import bpy
    o={x.name:x for x in bpy.data.objects if x.type=="MESH"}
    assert len(o)==42 and TARGET in o and FACE in o, (len(o),TARGET in o,FACE in o)
    assert all(n.startswith("PMT_F50_") for n in o)
    return o

def render_comparison(path):
    import bpy
    from mathutils import Vector
    obs=source_inventory()
    sc=bpy.context.scene
    old_hide={n:o.hide_render for n,o in obs.items()}
    old_camera=sc.camera
    old_engine=sc.render.engine
    old_width=sc.render.resolution_x
    old_height=sc.render.resolution_y
    old_percent=sc.render.resolution_percentage
    old_format=sc.render.image_settings.file_format
    old_path=sc.render.filepath
    cam_data=bpy.data.cameras.new("TEMP_INSTRUMENT_CLUSTER_QA_CAMERA")
    cam=bpy.data.objects.new("TEMP_INSTRUMENT_CLUSTER_QA_CAMERA",cam_data)
    bpy.context.collection.objects.link(cam)
    try:
        for n,o in obs.items():
            o.hide_render=(n not in [TARGET,FACE])
        cam.location=(-0.354,1.045,-0.14)
        cam.rotation_euler=(Vector((-0.354,0.745,-0.555))-cam.location).to_track_quat("-Z","Y").to_euler()
        cam_data.type="ORTHO";cam_data.ortho_scale=.56
        sc.camera=cam
        sc.render.engine="BLENDER_WORKBENCH"
        sc.display.shading.light="STUDIO"
        sc.display.shading.color_type="MATERIAL"
        sc.render.resolution_x=860;sc.render.resolution_y=640;sc.render.resolution_percentage=100
        sc.render.image_settings.file_format="PNG"
        sc.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
    finally:
        sc.camera=old_camera
        sc.render.engine=old_engine
        sc.render.resolution_x=old_width
        sc.render.resolution_y=old_height
        sc.render.resolution_percentage=old_percent
        sc.render.image_settings.file_format=old_format
        sc.render.filepath=old_path
        bpy.data.objects.remove(cam,do_unlink=True)
        bpy.data.cameras.remove(cam_data,do_unlink=True)
        for n,o in obs.items():o.hide_render=old_hide[n]
    assert path.is_file()
    return sha(path)

def edit():
    import bpy
    assert Path(bpy.data.filepath)==BASE
    assert sha(BASE)==SHA_INPUT and sha(PMT)==SHA_PMT
    assert not OUTPUT.exists(), "FAIL_CLOSED: v44 output already exists"
    obs=source_inventory()
    source=obs[TARGET]
    verts=source.data.vertices
    assert len(verts)==109 and len(source.data.polygons)==119
    before={n:sig(o) for n,o in obs.items()}
    before_png=render_comparison(OUT/"F50_InstrumentCluster_v44_BEFORE.png")
    # Native original profile proven by F50 material011 source vertex 52,34,35,37,39,41,42.
    # Existing paired brow/back profiles 32..43 form the surface. Photo: REF2 dashboard
    # closeup, authentic low black rounded instrument shroud; no fabricated dials.
    # Only local instrument brow zone; no outer dashboard, wheel or glass-adjacent vertices.
    profile={52,34,35,37,39,41,42}
    edited=[]
    edited_profile=[]
    distances=[]
    for v in verts:
        x,y,z=[float(t) for t in v.co]
        # Mark *existing* visible crown and backing strip inside instrument cluster bounds.
        if not (-.510<x<-.200 and .720<y<.805 and -.625<z<-.505):
            continue
        arch=max(0.0,1.0-abs((x+.3542765)/.162))
        depth=max(0.0,min(1.0,(-z-.506)/.13))
        # Raise outer shield 10-15 mm, return smoothly to both existing end contours.
        # Center crown remains modest in relation to actual photo black cluster brow.
        lift=0.012*(arch**.70)*(1.0-.25*depth)
        # Deepen the lip edge only on the leading existing native row, no new geometry.
        back=0.005*(arch**.8)*(1.0-depth)
        if lift<.002:continue
        v.co.y+=lift
        v.co.z-=back
        edited.append(v.index)
        distances.append(math.sqrt(lift*lift+back*back))
        if v.index in profile:edited_profile.append(v.index)
    assert len(edited)>=14 and len(edited_profile)>=5,(edited,edited_profile)
    assert max(distances)>.010 and max(distances)<.020
    assert all(verts[i].co.y<.82 for i in edited)
    after={n:sig(o) for n,o in obs.items()}
    changed=sorted(n for n in obs if before[n]!=after[n])
    assert changed==[TARGET],changed
    assert len(source.data.vertices)==109 and len(source.data.polygons)==119
    after_png=render_comparison(OUT/"F50_InstrumentCluster_v44_AFTER.png")
    assert {n:sig(o) for n,o in obs.items()}==after,"render changed native mesh"
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)
    assert OUTPUT.exists()
    receipt=dict(
        task_id="FERRARI16-SLOTC-F50-PMT011-INSTRUMENT-CLUSTER-V44-20261109",
        slot="C",vehicle="f50",component="instrument_cluster",
        status="COVERED_PARTIAL_QA",
        native_original_pmt_sha256=SHA_PMT,
        original_import_blend_sha256=SHA_IMPORT,
        input_blend=BASE.name,input_sha256=SHA_INPUT,
        output_blend=OUTPUT.name,output_sha256=sha(OUTPUT),
        original_mesh=TARGET,
        modified_objects=changed,
        source_mesh_fingerprints_before=before,
        source_mesh_fingerprints_after=after,
        unchanged_other_native_meshes=len(before)-len(changed),
        windshield_and_other_regions_untouched=True,
        changed_existing_vertices=len(edited),
        changed_vertex_indices=edited,
        native_profile_indices_changed=sorted(edited_profile),
        max_displacement_m=max(distances),
        preserved_native_topology={"vertices":109,"faces":119},
        private_photo_reference="03_F50/REF2_dashboard_closeup_dad64db8c0a5.jpg",
        geometry_design="Raised original gauge-crown support ~10-15 mm with tapered lip; no new faces or objects",
        before_png_sha256=before_png,after_png_sha256=after_png,
        blender_saved=True,independent_reopen="PENDING",exports=[],new_textures=[],
        full_vehicle_qa_pass=False,
        next="dashboard (P0 polish hold; guard policy must determine next dispatch)")
    RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding="utf-8")
    print("F50_INSTRUMENT_EDIT_OK",json.dumps({"changed_existing_vertices":len(edited),
        "displacement_m":max(distances),"sha256":sha(OUTPUT),"non_target_meshes_unchanged":41}))
def reopen():
    import bpy
    assert Path(bpy.data.filepath)==OUTPUT
    rec=json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert sha(OUTPUT)==rec["output_sha256"]
    now={n:sig(o) for n,o in source_inventory().items()}
    assert now==rec["source_mesh_fingerprints_after"],"fresh Blender reopen native fingerprints differ"
    assert rec["source_mesh_fingerprints_before"][TARGET]!=now[TARGET]
    rec["independent_reopen"]="PASS_BLENDER_4_5_15_SEPARATE_PROCESS"
    RECEIPT.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
    print("F50_INSTRUMENT_REOPEN_PASS",rec["output_sha256"])
def make_manifest():
    assert sha(OUTPUT)==json.loads(RECEIPT.read_text())["output_sha256"]
    data=OUTPUT.read_bytes()
    parts=[]
    for n,start in enumerate(range(0,len(data),262144),1):
        name=OUTPUT.stem+f".part{n:02d}.bin"
        chunk=data[start:start+262144]
        (OUT/name).write_bytes(chunk)
        parts.append({"file":name,"size":len(chunk),"offset":start,"sha256":hashlib.sha256(chunk).hexdigest()})
    m={
        "schema_version":1,"repository":"thp32tt/imsi1","branch":"main",
        "slot":"C","active_car_id":"f50","component":"instrument_cluster",
        "status":"COVERED_PARTIAL_QA","format":"plain_unencrypted_binary_parts",
        "binary_file":OUTPUT.name,"binary_size":len(data),"binary_sha256":sha(OUTPUT),
        "input_baseline":{"file":BASE.name,"sha256":SHA_INPUT},
        "original_native_game_resource":{"retained_on_n100":True,"file":PMT.name,"sha256":SHA_PMT},
        "original_import_blend_sha256":SHA_IMPORT,
        "chunk_size":262144,"parts":parts,
        "independent_blender_reopen":"PASS","full_vehicle_qa_pass":False,
        "next_component":"dashboard (P0_POLISH_HOLD; advance only per guard/controller)",
        "artifact_sha256":{x.name:sha(x) for x in [RECEIPT,OUT/"F50_InstrumentCluster_v44_BEFORE.png",OUT/"F50_InstrumentCluster_v44_AFTER.png"]},
        "protected_regions":["windshield","front_glass","A_pillars","dashboard","steering_wheel","exterior"]
    }
    (OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
    # Create source reassembler; it uses stdlib and verifies every plaintext part and whole digest.
    reasm='''#!/usr/bin/env python3
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
'''
    (OUT/"reassemble.py").write_text(reasm,encoding="utf-8")
    assert b"".join((OUT/p["file"]).read_bytes() for p in parts)==data
    assert sha(OUTPUT)==m["binary_sha256"]
    print("F50_MANIFEST_OK",m["binary_sha256"],len(parts))
def cli():
    assert len(sys.argv)==2 and sys.argv[1] in ["edit","reopen","package"]
    mode=sys.argv[1]
    if mode=="package":
        make_manifest()
        return
    assert sha(PMT)==SHA_PMT
    assert sha(BASE)==SHA_INPUT
    OUT.mkdir(parents=True,exist_ok=True)
    model=BASE if mode=="edit" else OUTPUT
    p=subprocess.run([BLENDER,"--background",str(model),"--python",str(Path(__file__)),"--",mode],
                     cwd=str(ROOT),capture_output=True,text=True,timeout=180)
    print(p.stdout[-12000:])
    if p.stderr:print(p.stderr[-5000:],file=sys.stderr)
    if p.returncode:raise SystemExit(p.returncode)
if __name__=="__main__":
    if "bpy" in sys.modules:
        mode=sys.argv[sys.argv.index("--")+1]
        if mode=="edit":edit()
        elif mode=="reopen":reopen()
        else:raise ValueError(mode)
    else:cli()