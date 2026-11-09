#!/usr/bin/env python3
"""One-shot, source-only import of verified OutRun 2006 Ferrari 360 Spider native .sz PMT.

Reads the original N100 PMT without writing to it. Exact source local coordinates,
triangle indices, PMT object/group IDs, first and second UV sets, native normals,
material group identifiers, and per-object SHA fingerprints are retained.
No mesh/transform edits, fabricated objects, conversion/export, or textures.
Run inside Blender 4.5.15: --background --python <this-script> -- --import|--verify ...
"""
from __future__ import annotations
import sys, json, math, hashlib, struct, zlib
from pathlib import Path
import bpy

EXPECTED_SHA = "a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6"
EXPECTED_SOURCE = Path("/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_360sp_pmt.sz")
MAX_PMT_BYTES = 128 * 1024 * 1024
MAX_VERTEX_BYTES = 64 * 1024 * 1024

# Original PMT parser from private N100 pmt_export_base.py, standard-library
# read-only geometry portion, extended ONLY for native FVF 0x212 stride 40:
# XYZ/normal/UV0/UV1; no geometry simplification or procedural generation.
def u16(data, off):
    if off < 0 or off + 2 > len(data):
        raise ValueError("u16 out of bounds")
    return struct.unpack_from("<H", data, off)[0]


def u32(data, off):
    if off < 0 or off + 4 > len(data):
        raise ValueError("u32 out of bounds")
    return struct.unpack_from("<I", data, off)[0]


def i32(data, off):
    if off < 0 or off + 4 > len(data):
        raise ValueError("i32 out of bounds")
    return struct.unpack_from("<i", data, off)[0]


def bounds(data, off, length):
    if off < 0 or length < 0 or off + length > len(data):
        raise ValueError("PMT segment out of bounds")
    return off


def unpack(data, fmt, off):
    bounds(data, off, struct.calcsize(fmt))
    return struct.unpack_from(fmt, data, off)


def open_pmt(path):
    raw = path.read_bytes()
    if raw[:2] not in (bytes((0x78,0x9c)), bytes((0x78,0xda)), bytes((0x78,0x01))):
        raise ValueError("expected zlib-compressed .sz")
    d = zlib.decompress(raw, max_length=MAX_PMT_BYTES) if hasattr(zlib, "max_length") else zlib.decompress(raw)
    if len(d) > MAX_PMT_BYTES:
        raise ValueError("expanded PMT exceeds budget")
    obj_count, tex_count, syslen, vidlen = unpack(d, "<4I", 0)
    if obj_count > 4096 or tex_count > 4096 or syslen + vidlen + 16 != len(d):
        raise ValueError("invalid PMT header")
    system, video = d[16:16 + syslen], d[16 + syslen:]
    if u32(system, 4) != obj_count or u32(system, 8) != tex_count:
        raise ValueError("PMT counts disagree")
    xpr_off = 24 + 60 * obj_count + 4 * (tex_count + 1)
    if system[xpr_off:xpr_off + 4] != b"XPR0":
        raise ValueError("missing XPR0")
    data_size = u32(system, xpr_off + 4) - u32(system, xpr_off + 8)
    offsets = [u32(system, xpr_off + 12 + 20 * i + 4) for i in range(tex_count)]
    if any(off > data_size for off in offsets):
        raise ValueError("invalid XPR texture offset")
    return {"obj_count": obj_count, "tex_count": tex_count,
            "system": system, "video": video, "offsets": offsets,
            "data_size": data_size}



def triangulate(raw, topology):
    out = []
    def emit(a, b, c):
        if a != b and b != c and a != c:
            out.extend((a, b, c))
    if topology == 5:
        for i in range(0, len(raw), 3):
            emit(*raw[i:i + 3])
    elif topology == 6:
        for i in range(len(raw) - 2):
            a, b, c = raw[i:i + 3]
            emit(b, a, c) if i % 2 else emit(a, b, c)
    elif topology == 8:
        for i in range(0, len(raw), 4):
            a, b, c, d = raw[i:i + 4]
            emit(a, b, c)
            emit(a, c, d)
    else:
        raise ValueError("unsupported primitive topology %s" % topology)
    return out


def decode_object(asset, oi):
    sys, vid = asset["system"], asset["video"]
    if oi < 0 or oi >= asset["obj_count"]:
        raise ValueError("object index out of range")
    q = unpack(sys, "<15I", 24 + oi * 60)
    h = unpack(sys, "<13I", q[5])
    fmts = []
    for j in range(h[9]):
        fs = unpack(sys, "<11I", q[12] + j * 44)
        stream, vf, stride, shader = fs[0], fs[8], fs[9], fs[10]
        if stream != 1 or shader != 0 or (vf, stride) not in ((0x12, 24), (0x112, 32), (0x212, 40)):
            raise ValueError("unsupported Dino FVF/stride/shader: %s" % ((stream, vf, stride, shader),))
        ip = u32(sys, q[1] + j * 4)
        ixoff = u32(sys, ip + 4)
        vp = u32(sys, q[2] + j * 16)
        voff = u32(sys, vp + 4)
        bounds(sys, ixoff, fs[6])
        bounds(vid, voff, fs[7])
        if fs[7] > MAX_VERTEX_BYTES or fs[7] % stride or fs[6] % 2:
            raise ValueError("invalid format buffers")
        fmts.append((vf, stride, ixoff, voff, fs[6] // 2, fs[7] // stride))
    result = []
    if (q[10] - q[9]) % 20 or q[10] < q[9]:
        raise ValueError("invalid vertex group table")
    for gi, goff in enumerate(range(q[9], q[10], 20)):
        fidx, first0, first1, count0, count1 = unpack(sys, "<5I", goff)
        if fidx >= len(fmts):
            raise ValueError("invalid format index")
        vf, stride, ixoff, voff, nic, nvert = fmts[fidx]
        for alpha, first, count in ((0, first0, count0), (1, first1, count1)):
            if count and first + count > h[10]:
                raise ValueError("invalid material group interval")
            for mgi in range(first, first + count):
                mg = unpack(sys, "<8I", q[10] + mgi * 32)
                base, mat, prstart, prcount = mg[:4]
                if mat >= h[11]:
                    raise ValueError("invalid material index")
                global_ids = []
                for pj in range(prcount):
                    pr = unpack(sys, "<4I", q[11] + (prstart + pj) * 16)
                    top, istart, icount = pr[0], pr[1], pr[2]
                    n = icount * 3 if top == 5 else icount + 2 if top == 6 else icount * 4 if top == 8 else 0
                    if n <= 0 or istart + n > nic:
                        raise ValueError("invalid primitive index interval")
                    ids = [base + u16(sys, ixoff + 2 * (istart + i)) for i in range(n)]
                    if any(v >= nvert for v in ids):
                        raise ValueError("primitive index exceeds vertices")
                    global_ids.extend(triangulate(ids, top))
                if not global_ids:
                    continue
                mapping = {}
                positions, normals, uvs, uvs2, indices = [], [], [], [], []
                for old in global_ids:
                    if old not in mapping:
                        off = voff + old * stride
                        v = unpack(vid, "<6f", off)
                        if not all(math.isfinite(x) and abs(x) <= 10000 for x in v):
                            raise ValueError("invalid vertex float")
                        pos, norm = v[:3], v[3:6]
                        uv = unpack(vid, "<2f", off + 24) if vf in (0x112, 0x212) else (0., 0.)
                        uv2 = unpack(vid, "<2f", off + 32) if vf == 0x212 else (0., 0.)
                        if not all(math.isfinite(x) and abs(x) <= 10000 for x in uv + uv2):
                            raise ValueError("invalid UV")
                        mapping[old] = len(positions)
                        positions.append(tuple(pos))
                        normals.append(tuple(norm))
                        uvs.append(tuple(uv))
                        uvs2.append(tuple(uv2))
                    indices.append(mapping[old])
                moff = q[13] + mat * 88
                tex_index = i32(sys, moff + 24)
                if tex_index < 0 or tex_index >= asset["tex_count"]:
                    tex_index = None
                colorid = i32(sys, moff)
                c = unpack(sys, "<4f", q[14] + 72 * colorid) if 0 <= colorid < h[12] else (1., 1., 1., 1.)
                if not all(math.isfinite(x) for x in c):
                    c = (1., 1., 1., 1.)
                result.append({
                    "name": "object%02d_group%02d_material%03d_a%d" % (oi, gi, mgi, alpha),
                    "object": oi, "group": gi, "material_group": mgi,
                    "tex_index": tex_index, "color": [min(1, max(0, float(x))) for x in c],
                    "alpha": alpha, "vertices": positions, "normals": normals,
                    "uvs": uvs, "uvs2": uvs2, "indices": indices
                })
    return result




def native_mesh_hash(verts, indices):
    d = hashlib.sha256()
    d.update(struct.pack("<II", len(verts), len(indices) // 3))
    for v in verts:
        d.update(struct.pack("<3f", *v))
    for idx in indices:
        d.update(struct.pack("<I", idx))
    return d.hexdigest()

def native_aux_hash(norms, uv0, uv1):
    d=hashlib.sha256()
    for v in norms: d.update(struct.pack("<3f",*v))
    for v in uv0: d.update(struct.pack("<2f",*v))
    for v in uv1: d.update(struct.pack("<2f",*v))
    return d.hexdigest()

def identity(p):
    return "PMT_" + p["name"]

def read_native():
    assert EXPECTED_SOURCE.is_file(), "BLOCKED missing original PMT"
    assert hashlib.sha256(EXPECTED_SOURCE.read_bytes()).hexdigest() == EXPECTED_SHA, "BLOCKED original PMT SHA"
    a=open_pmt(EXPECTED_SOURCE)
    parts=[]
    for i in range(a["obj_count"]):
        group=decode_object(a,i)  # fail-closed on ANY unsupported native object
        for part in group:
            assert len(part["indices"])%3==0 and len(part["vertices"])>0
            assert len(part["uvs"])==len(part["vertices"])==len(part["normals"])==len(part["uvs2"])
            parts.append(part)
    assert len(set(identity(x) for x in parts))==len(parts) and len(parts)>=2
    return a,parts

def actual_geometry(obj):
    m=obj.data
    verts=[tuple(v.co) for v in m.vertices]
    ids=[int(i) for poly in m.polygons for i in poly.vertices]
    return native_mesh_hash(verts,ids)

def actual_aux(obj):
    m=obj.data
    normal=m.attributes.get("PMT_ORIGINAL_NORMAL")
    assert normal and len(normal.data)==len(m.vertices)
    norms=[tuple(e.vector) for e in normal.data]
    uv0=[None]*len(m.vertices); uv1=[None]*len(m.vertices)
    for idx, layer_name, dest in ((0,"PMT_UV0",uv0),(1,"PMT_UV1",uv1)):
        layer=m.uv_layers.get(layer_name)
        assert layer is not None
        for loop in m.loops:
            vi=loop.vertex_index
            uv=tuple(layer.data[loop.index].uv)
            if dest[vi] is None:dest[vi]=uv
            else:assert dest[vi]==uv,"unexpected per-loop UV seam"
        assert all(v is not None for v in dest)
    return native_aux_hash(norms,uv0,uv1)

def create():
    a,parts=read_native()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # No transform adjustment or additions; original PMT coordinates and face order.
    native_hashes={}; aux_hashes={}; entries=[]
    for p in parts:
        name=identity(p)
        mesh=bpy.data.meshes.new(name + "_native")
        vertices=p["vertices"]
        faces=[tuple(p["indices"][i:i+3]) for i in range(0,len(p["indices"]),3)]
        mesh.from_pydata(vertices,[],faces)
        assert len(mesh.vertices)==len(vertices) and len(mesh.polygons)==len(faces)
        uv0=mesh.uv_layers.new(name="PMT_UV0")
        uv1=mesh.uv_layers.new(name="PMT_UV1")
        normal=mesh.attributes.new(name="PMT_ORIGINAL_NORMAL",type="FLOAT_VECTOR",domain="POINT")
        for vi,v in enumerate(p["normals"]):normal.data[vi].vector=v
        for loop in mesh.loops:
            vi=loop.vertex_index
            uv0.data[loop.index].uv=p["uvs"][vi]
            uv1.data[loop.index].uv=p["uvs2"][vi]
        ob=bpy.data.objects.new(name,mesh)
        bpy.context.scene.collection.objects.link(ob)
        ob["native_pmt_id"]=p["name"]
        ob["native_object_index"]=int(p["object"])
        ob["native_group_index"]=int(p["group"])
        ob["native_material_group"]=int(p["material_group"])
        ob["native_alpha_group"]=int(p["alpha"])
        ob["native_texture_index"]=int(p["tex_index"]) if p["tex_index"] is not None else -1
        ob["native_pmt_sha256"]=EXPECTED_SHA
        ob["source_geometry_unmodified"]=True
        assert tuple(ob.matrix_world)==tuple(__import__("mathutils").Matrix.Identity(4))
        expected_geom=native_mesh_hash(vertices,p["indices"])
        expected_aux=native_aux_hash(p["normals"],p["uvs"],p["uvs2"])
        assert actual_geometry(ob)==expected_geom,"source geometry import mismatch "+name
        assert actual_aux(ob)==expected_aux,"source native normal/UV mismatch "+name
        ob["native_mesh_fingerprint_sha256"]=expected_geom
        ob["native_attributes_fingerprint_sha256"]=expected_aux
        native_hashes[name]=expected_geom;aux_hashes[name]=expected_aux
        entries.append([name,len(vertices),len(faces),int(p["object"])])
    assert all(ob.type=="MESH" for ob in bpy.data.objects)
    assert len(entries)==len(bpy.data.objects)
    result={"status":"SOURCE_VERIFIED_CANDIDATE","car_id":"360spider","slot":"A",
        "source_pmt_file":str(EXPECTED_SOURCE),"source_pmt_sha256":EXPECTED_SHA,
        "source_pmt_bytes":EXPECTED_SOURCE.stat().st_size,
        "pmt_objects":a["obj_count"],"native_mesh_count":len(entries),
        "native_vertex_count":sum(x[1] for x in entries),
        "native_triangle_count":sum(x[2] for x in entries),
        "original_mesh_object_ids":list(native_hashes),
        "native_mesh_fingerprints":native_hashes,"native_attribute_fingerprints":aux_hashes,
        "mesh_geometry_changed":False,"original_resource_modified":False,
        "windshield_or_adjacent_mesh_modified":False,"synthetic_objects":0,
        "intermediate_pmt_or_private_photos_published":False}
    out=Path(sys.argv[sys.argv.index("--")+2])
    receipt=Path(sys.argv[sys.argv.index("--")+3])
    out.parent.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
    assert out.is_file()
    result["blend_file"]=str(out)
    result["blend_sha256"]=hashlib.sha256(out.read_bytes()).hexdigest()
    receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("PMT_SOURCE_IMPORT_OK",json.dumps({"meshes":len(entries),"vertices":result["native_vertex_count"],"triangles":result["native_triangle_count"],"sha256":result["blend_sha256"]}),flush=True)

def verify():
    _, parts=read_native()
    map_parts={identity(p):p for p in parts}
    object_map={o.name:o for o in bpy.data.objects}
    assert object_map.keys()==map_parts.keys(),"native PMT objects not 1:1"
    for name,p in map_parts.items():
        ob=object_map[name]
        assert ob.type=="MESH" and tuple(ob.matrix_world)==tuple(__import__("mathutils").Matrix.Identity(4)),name+" transform changed"
        assert ob.get("native_pmt_id")==p["name"] and ob.get("native_pmt_sha256")==EXPECTED_SHA
        assert actual_geometry(ob)==native_mesh_hash(p["vertices"],p["indices"])==ob.get("native_mesh_fingerprint_sha256"),name+" geometry fingerprint"
        assert actual_aux(ob)==native_aux_hash(p["normals"],p["uvs"],p["uvs2"])==ob.get("native_attributes_fingerprint_sha256"),name+" normals or UV"
    print("PMT_SOURCE_INDEPENDENT_REOPEN_PASS",json.dumps({"mesh_count":len(map_parts),"source_sha256":EXPECTED_SHA}),flush=True)

if __name__=="__main__":
    tail=sys.argv[sys.argv.index("--")+1:]
    assert tail[0] in ("--import","--verify")
    create() if tail[0]=="--import" else verify()