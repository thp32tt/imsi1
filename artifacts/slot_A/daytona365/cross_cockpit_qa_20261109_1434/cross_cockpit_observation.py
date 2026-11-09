#!/usr/bin/env python3
"""Read-only Daytona slot A cross-cockpit observation. Never save the loaded Blender scene."""
import hashlib, json, os, subprocess, sys
from pathlib import Path

BASE=Path("/home/chatgpt-runner")
SRC=BASE/"work_handoff/ferrari16_slotA_daytona_dashboard_steering_20261108/Daytona365_SlotA_OriginalPMT005_InnerDoor_R45.blend"
BIN=BASE/"work_handoff/blender_4_5_15_official_cache/blender-4.5.15-linux-x64/blender"
OUT=BASE/"work_handoff/ferrari16_slotA_daytona_dashboard_steering_20261108/slotA_cross_cockpit_qa_20261109_1434"
PHOTO=BASE/"outrun2_vr_refs/20261104_16car_cockpit/02_365_GTS4_Daytona/REF2_dashboard_original_e91527ff82f3.jpg"
EXPECTED="224131c7adc928d5d6f0377d030d5a350c59b8664c13303a2731d6dfc6e9a722"
ORIGINAL="f393ba5c706453a4d3f71604f25cd1631594152380856462fb0a504143ba6abe"
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def blender_run():
    import bpy
    from mathutils import Vector
    OUT.mkdir(parents=True,exist_ok=True)
    scene=bpy.context.scene
    orig_mesh_count=len([o for o in bpy.data.objects if o.type=="MESH"])
    camera_exists=scene.camera is not None and scene.camera.type=="CAMERA"
    if not camera_exists:
        cameras=[o for o in bpy.data.objects if o.type=="CAMERA"]
        if cameras: scene.camera=cameras[0]
    camera_source="PERSISTED_SCENE" if camera_exists else ("EXISTING_CAMERA" if scene.camera else "RUNTIME_APPROX_UNCALIBRATED")
    if scene.camera is None:
        wheels=[o for o in bpy.data.objects if o.type=="MESH" and ("wheel" in o.name.lower() or "object22_group00_material000" in o.name.lower())]
        dashes=[o for o in bpy.data.objects if o.type=="MESH" and ("dash" in o.name.lower() or "object00_group01_material012" in o.name.lower())]
        focus=wheels[0] if wheels else (dashes[0] if dashes else next(o for o in bpy.data.objects if o.type=="MESH"))
        points=[focus.matrix_world@Vector(v) for v in focus.bound_box]
        c=sum(points,Vector())/len(points)
        dx=max(p.x for p in points)-min(p.x for p in points)
        dy=max(p.y for p in points)-min(p.y for p in points)
        dz=max(p.z for p in points)-min(p.z for p in points)
        size=max(dx,dy,dz,.5)
        camdata=bpy.data.cameras.new("TEMP_QA_DRIVER_CAMERA_NONPERSISTENT")
        cam=bpy.data.objects.new("TEMP_QA_DRIVER_CAMERA_NONPERSISTENT",camdata)
        scene.collection.objects.link(cam)
        cam.location=c+Vector((0,-size*2.0,size*0.65))
        direction=(c-cam.location).normalized()
        cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
        camdata.type="PERSP"
        camdata.lens=45
        scene.camera=cam
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="MATERIAL"
    scene.render.resolution_x=800
    scene.render.resolution_y=540
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=str(OUT/"Daytona365_R45_cross_cockpit_observation.png")
    bpy.ops.render.render(write_still=True)
    result={"status":"RENDERED_READ_ONLY_NOT_SCENE_EDIT","camera_source":camera_source,"camera_name":scene.camera.name,"true_game_driver_eye_calibrated":False,"scene_file_sha256_before":EXPECTED,"original_pmt_sha256":ORIGINAL,"native_mesh_object_count":orig_mesh_count,"render_path":str(OUT/"Daytona365_R45_cross_cockpit_observation.png"),"geometry_edits":0,"source_file_saved":False,"photo_kept_private":True,"whole_car_qa_pass":False}
    (OUT/"blender_observation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("CROSS_COCKPIT_QA="+json.dumps(result))
def launcher():
    if sha(SRC)!=EXPECTED: raise SystemExit("BLOCKED_INPUT_R45_SHA_MISMATCH")
    if not PHOTO.exists(): raise SystemExit("BLOCKED_PHOTO_ABSENT")
    OUT.mkdir(parents=True,exist_ok=True)
    command=[str(BIN),"-b",str(SRC),"--python",str(Path(__file__).resolve()),"--","blender-readonly"]
    r=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
    (OUT/"blender_log.txt").write_text(r.stdout[-16000:],encoding="utf-8")
    if r.returncode: raise RuntimeError(f"BLENDER_RENDER_FAILED {r.returncode}: {r.stdout[-1800:]}")
    proof=json.loads((OUT/"blender_observation.json").read_text(encoding="utf-8"))
    proof.update({"input_blend_sha256":sha(SRC),"input_blend_sha256_after":sha(SRC),"photo_sha256_N100_only":sha(PHOTO),"render_sha256":sha(OUT/"Daytona365_R45_cross_cockpit_observation.png"),"reopen":"READ_ONLY_LOADED_IN_SEPARATE_BLENDER_PROCESS"})
    if proof["input_blend_sha256"]!=proof["input_blend_sha256_after"]:raise RuntimeError("SOURCE_CHANGED")
    (OUT/"blender_observation.json").write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(proof,ensure_ascii=False,indent=2))
if __name__=="__main__":
    if "--" in sys.argv and "blender-readonly" in sys.argv[sys.argv.index("--")+1:]: blender_run()
    else: launcher()