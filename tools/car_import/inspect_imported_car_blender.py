#!/usr/bin/env python3
"""Read-only role and mesh audit of a KN5-imported Blender scene.

Run: blender --background imported.blend --python inspect_imported_car_blender.py -- --output report.json
No mesh edits, PMT export, or in-game installation are done here.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

try:
    import bpy
except ImportError as exc:
    raise SystemExit('Run inside Blender after importing the complete car KN5 files') from exc

WHEELS = ('WHEEL_LF', 'WHEEL_RF', 'WHEEL_LR', 'WHEEL_RR')
ROLES = WHEELS + ('COCKPIT_HR', 'COCKPIT_LR', 'STEER_HR', 'STEER_LR')


def chain(obj):
    while obj is not None:
        yield obj
        obj = obj.parent


def role_of(obj):
    for ancestor in chain(obj):
        name = ancestor.name.upper().split('.')[0]
        if name in ROLES:
            return name
    return None


def inspect_scene():
    nodes = {role: [] for role in ROLES}
    objects = []
    triangles = 0
    materials = set()
    missing_uv = []
    loose_meshes = []
    texture_refs = set()
    for obj in bpy.data.objects:
        role = role_of(obj)
        if role:
            nodes[role].append(obj.name)
        if obj.type != 'MESH':
            continue
        mesh = obj.data
        tri_count = sum(max(0, len(poly.vertices) - 2) for poly in mesh.polygons)
        triangles += tri_count
        if not len(mesh.uv_layers):
            missing_uv.append(obj.name)
        if not role:
            loose_meshes.append(obj.name)
        for material in mesh.materials:
            if material:
                materials.add(material.name)
                if material.use_nodes and material.node_tree:
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                            texture_refs.add(node.image.name)
        objects.append({
            'name': obj.name, 'role': role,
            'vertices': len(mesh.vertices), 'triangles': tri_count,
            'uv_layers': len(mesh.uv_layers), 'material_slots': len(mesh.materials),
            'origin_world': [round(float(x), 6) for x in obj.matrix_world.translation],
            'parent': obj.parent.name if obj.parent else None,
        })
    absent_wheels = [r for r in WHEELS if not nodes[r]]
    missing_cockpit = not nodes['COCKPIT_HR'] and not nodes['COCKPIT_LR']
    missing_steer = not nodes['STEER_HR'] and not nodes['STEER_LR']
    warnings = []
    if absent_wheels:
        warnings.append('Missing wheel nodes: ' + ', '.join(absent_wheels))
    if missing_cockpit:
        warnings.append('Missing COCKPIT_HR/COCKPIT_LR node')
    if missing_steer:
        warnings.append('Missing STEER_HR/STEER_LR node')
    if missing_uv:
        warnings.append(f'{len(missing_uv)} mesh objects have no UV layer')
    if not loose_meshes:
        warnings.append('Exterior cannot be assigned; no loose body meshes found')
    return {
        'schema': 'outrun-ac-full-car-scene-v1',
        'status': ('NEEDS_OUTRUN_MAPPING' if
                   objects and not absent_wheels and not missing_cockpit and
                   not missing_steer and loose_meshes else 'BLOCKED_SCENE_ROLES'),
        'blend_file': Path(bpy.data.filepath).name,
        'mesh_objects': len(objects),
        'draw_triangles_estimate': triangles,
        'materials': sorted(materials),
        'image_datablocks': sorted(texture_refs),
        'role_nodes': nodes,
        'meshes_without_uv': missing_uv,
        'unassigned_mesh_names': loose_meshes,
        'objects': objects,
        'warnings': warnings,
        'required_next_checks': [
            'LOD grouping', 'geometry bounds and scale', 'wheel and steering pivots',
            'triangle winding', 'normal preservation', 'material alpha',
            'PMT texture formats', 'game mounting', 'both VR eyes'],
        'not_exported_to_pmt': True,
        'source_modified': False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    args = parser.parse_args(argv)
    report = inspect_scene()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf-8')
    print('Full-car scene inspection:', report['status'],
          'triangles=', report['draw_triangles_estimate'])
    return 0 if report['status'] == 'NEEDS_OUTRUN_MAPPING' else 2


if __name__ == '__main__':
    raise SystemExit(main())
