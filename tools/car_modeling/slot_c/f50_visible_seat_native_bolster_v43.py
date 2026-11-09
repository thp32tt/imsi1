# Ferrari F50 SLOT C visible_seat: original PMT-native geometry edit (2026-11-09).
# This file only edits 2 existing 64-vertex seat-support components in PMT_F50_object00_group01_material023_a0.
# No objects, polygons, textures, PBR, wheels, windscreen geometry or exports are created.
import bpy,hashlib,json,math,struct
from pathlib import Path
from mathutils import Vector

ROOT=Path("/home/chatgpt-runner/work_handoff/ferrari16_slotC_f50_source_audit_20261108")
SOURCE=ROOT/"F50_OriginalPMT_InnerDoor_UpperRail_v40.blend"
OUTPUT=ROOT/"F50_OriginalPMT_VisibleSeat_Bolster_v43.blend"
TARGET="PMT_F50_object00_group01_material023_a0"
NATIVE_SHA="10daa1312b6cff0267b38b4c440c6007c68b470a225ca15f0c324876fd80aeab"
SOURCE_SHA="03b96b1eb2293c151c60133919380055fa8393372b0acbf18045edf25faa949a"
assert bpy.data.filepath==str(SOURCE),(bpy.data.filepath,SOURCE)
assert not OUTPUT.exists(),"Fail closed: v43 checkpoint already exists"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
assert hashlib.sha256(Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_f50_pmt.sz").read_bytes()).hexdigest()==NATIVE_SHA

def sig(obj):
    h=hashlib.sha256()
    h.update(obj.name.encode())
    h.update(struct.pack("<16d",*[float(z) for row in obj.matrix_world for z in row]))
    h.update(struct.pack("<QQ",len(obj.data.vertices),len(obj.data.polygons)))
    for v in obj.data.vertices: h.update(struct.pack("<3d",*map(float,v.co)))
    for f in obj.data.polygons:
        h.update(struct.pack("<I",len(f.vertices)))
        for ix in f.vertices:h.update(struct.pack("<I",ix))
    return h.hexdigest()
objects={o.name:o for o in bpy.data.objects if o.type=="MESH"}
assert len(objects)==42, "Source native 42 mesh objects required"
assert TARGET in objects
before={name:sig(o) for name,o in objects.items()}
ob=objects[TARGET]; me=ob.data
assert len(me.vertices)==207 and len(me.polygons)==211
# Edge-connected source components. Preserve object, topology and non-seat components.
par=list(range(len(me.vertices)))
def find(x):
    while par[x]!=x:par[x]=par[par[x]];x=par[x]
    return x
def union(a,b):
    a=find(a);b=find(b)
    if a!=b:par[b]=a
for face in me.polygons:
    inds=list(face.vertices)
    for ix in inds[1:]: union(inds[0],ix)
components={}
for v in me.vertices: components.setdefault(find(v.index),[]).append(v.index)
seat_components=[]
for indices in components.values():
    if len(indices)!=64:continue
    p=[me.vertices[i].co for i in indices]
    c=[sum(v[k] for v in p)/len(p) for k in range(3)]
    width=max(v.x for v in p)-min(v.x for v in p)
    height=max(v.y for v in p)-min(v.y for v in p)
    length=max(v.z for v in p)-min(v.z for v in p)
    if .24<abs(c[0])<.48 and .72<height<.85 and .43<width<.55 and .63<length<.78:
        seat_components.append((indices,c,width,height,length))
assert len(seat_components)==2,[(len(x),c) for x,c,*_ in seat_components]
assert seat_components[0][1][0]*seat_components[1][1][0]<0
edited=set();changes=[]
for indices,center,width,height,length in seat_components:
    side=1 if center[0]>0 else -1
    ys=[me.vertices[i].co.y for i in indices]
    ymin,ymax=min(ys),max(ys)
    for i in indices:
        p=me.vertices[i].co
        u=(p.y-ymin)/(ymax-ymin)
        lateral=min(1.0,abs(p.x-center[0])/(width*.5))
        edge=max(0.0,min(1.0,(lateral-.20)/.78))
        edge=edge*edge*(3-2*edge)
        middle=math.exp(-((u-.53)/.22)**2)
        shoulder=math.exp(-((u-.84)/.16)**2)
        # F50 photo reference: contoured black bucket-seat side supports and high shoulders.
        # No generated surface: re-position existing verified original game seat-ring vertices only.
        dx=side*(.020*edge*middle+.014*edge*shoulder-.004*(1-edge)*middle)
        dy=.011*shoulder*(.35+.65*edge)
        dz=-.015*middle*(.35+.65*edge)
        if max(abs(dx),abs(dy),abs(dz))<0.0002:continue
        old=p.copy()
        p.x+=dx; p.y+=dy; p.z+=dz
        edited.add(i)
        changes.append(float((p-old).length))
assert len(edited)>=45 and max(changes)<.031
after={name:sig(o) for name,o in objects.items()}
changed_objects=sorted(n for n in objects if before[n]!=after[n])
assert changed_objects==[TARGET],changed_objects
assert all(len(me.polygons)==211 for _ in [0])
# Write before/after matching camera renders without committing any extra mesh or camera.
def render(path,source):
    from mathutils import Vector
    # Mesh deformation only; all other original meshes are hidden in the QA preview, never modified.
    restore={o.name:o.hide_render for o in objects.values()}
    for o in objects.values():
        o.hide_render=(o.name!=TARGET)
        if o.name==TARGET:o.color=(.68,.18,.16,1)
    camera_data=bpy.data.cameras.new("TEMP_QA_seat_camera")
    camera=bpy.data.objects.new("TEMP_QA_seat_camera",camera_data)
    bpy.context.collection.objects.link(camera)
    sc=bpy.context.scene; prior_cam=sc.camera;sc.camera=camera
    camera.location=(2.3,1.8,-1.9)
    camera.rotation_euler=(Vector((0,.55,-.08))-camera.location).to_track_quat("-Z","Y").to_euler()
    camera_data.type="ORTHO";camera_data.ortho_scale=2.2
    prev_engine=sc.render.engine
    sc.render.engine="BLENDER_WORKBENCH"
    sc.display.shading.light="STUDIO"
    sc.display.shading.color_type="OBJECT"
    sc.render.resolution_x=950;sc.render.resolution_y=650;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format="PNG";sc.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    sc.render.engine=prev_engine
    sc.camera=prior_cam
    bpy.data.objects.remove(camera,do_unlink=True)
    bpy.data.cameras.remove(camera_data,do_unlink=True)
    for o in objects.values():o.hide_render=restore[o.name]
    return hashlib.sha256(path.read_bytes()).hexdigest()

# Reconstruct true original coordinates for baseline QA render only; restore changed coords.
restore_seat={i:me.vertices[i].co.copy() for i in edited}
# Get original vertices from the untouched source by difference using recorded per-vertex offsets.
# For deterministic provenance, hold exact old coords from a second original source mesh object lookup.
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)
saved_sha=hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
# Load v40 in a separate Blender process to create the BEFORE image, not in this process.
after_render_sha=render(ROOT/"F50_VisibleSeat_v43_AFTER.png",False)
receipt={
 "task_id":"FERRARI16-SLOTC-F50-VISIBLE-SEAT-PMT023-V43-20261109",
 "slot":"C","vehicle":"f50","component":"visible_seat","status":"COVERED_PARTIAL_QA",
 "native_original_pmt_sha256":NATIVE_SHA,
 "original_import_blend_sha256":"d82b3d024a812126da5b38c56572cfc326fbe3d1b5c0ddf8cad4cbd855119d31",
 "input_blend":SOURCE.name,"input_sha256":SOURCE_SHA,
 "output_blend":OUTPUT.name,"output_sha256":saved_sha,
 "source_native_mesh":"object00_group01_material023_a0",
 "original_mesh":"PMT_F50_object00_group01_material023_a0",
 "seat_components":2,"source_vertices_per_seat":64,
 "changed_existing_vertices":len(edited),"max_displacement_m":max(changes),
 "unchanged_other_native_meshes":41,
 "modified_objects":changed_objects,
 "nonseat_components_within_target_unchanged":True,
 "source_mesh_fingerprints_before":before,
 "source_mesh_fingerprints_after":after,
 "render_after_sha256":after_render_sha,
 "windshield_and_other_regions_untouched":True,
 "blender_saved":True,
 "independent_reopen":"PENDING_SEPARATE_PROCESS",
 "photo_reference_private":"03_F50/REF5_mecum_interior_02_552c4a048.jpg",
 "visual_qa":"PARTIAL_UNCALIBRATED",
 "full_vehicle_qa_pass":False,
 "next":"instrument_cluster",
 "exports":[],"new_textures":[]}
(ROOT/"F50_VisibleSeat_v43_Receipt.json").write_text(json.dumps(receipt,indent=2),encoding="utf8")
print("F50_SEAT_MATERIAL_EDIT_PASS",len(edited),max(changes),saved_sha)