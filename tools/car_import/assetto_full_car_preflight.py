#!/usr/bin/env python3
"""Read-only inventory of a locally owned Assetto Corsa complete car directory.

Does not read geometry from KN5, alter game files or claim OutRun compatibility.
Only writes a sanitized JSON manifest when --output is supplied.
"""
from __future__ import annotations

import argparse
import configparser
import hashlib
import json
from pathlib import Path
import sys

MAX_KN5_FILES = 128
MAX_KN5_BYTES = 1024 * 1024 * 1024


class InputError(ValueError):
    pass


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _safe_file(root: Path, name: str) -> Path:
    if not name or Path(name).name != name or name in {'.', '..'}:
        raise InputError(f'LOD entry is not a local filename: {name!r}')
    candidate = root / name
    if candidate.is_symlink() or not candidate.is_file():
        raise InputError(f'LOD entry missing or symbolic link: {name}')
    if candidate.suffix.casefold() != '.kn5':
        raise InputError(f'LOD entry is not KN5: {name}')
    return candidate


def _lod_ini(root: Path) -> tuple[list[dict], list[str]]:
    warnings: list[str] = []
    ini = root / 'data' / 'lods.ini'
    if ini.is_symlink():
        raise InputError('lods.ini symbolic links are not accepted')
    if not ini.is_file():
        return [], ['No unpacked data/lods.ini; fallback LOD selection is heuristic']
    config = configparser.ConfigParser(interpolation=None, strict=True)
    try:
        with ini.open('r', encoding='utf-8-sig') as stream:
            config.read_file(stream)
    except (OSError, UnicodeError, configparser.Error) as exc:
        raise InputError(f'Invalid lods.ini: {exc}') from exc
    levels: list[dict] = []
    for section in config.sections():
        if section.upper().startswith('LOD_'):
            if not section[4:].isdigit():
                warnings.append(f'Ignored malformed LOD section {section}')
                continue
            name = config.get(section, 'FILE', fallback='').strip()
            if not name:
                raise InputError(f'{section} is missing FILE')
            _safe_file(root, name)
            levels.append({'level': int(section[4:]), 'file': name})
    levels.sort(key=lambda x: x['level'])
    if len({x['level'] for x in levels}) != len(levels):
        raise InputError('Duplicate numbered LOD sections')
    if levels and levels[0]['level'] != 0:
        raise InputError('LOD list has no LOD_0')
    if not levels:
        warnings.append('lods.ini has no valid LOD sections')
    return levels, warnings


def _select_primary(kn5: list[Path], root: Path, lod: list[dict]) -> tuple[Path | None, str]:
    index = {p.name.casefold(): p for p in kn5}
    if lod:
        return index.get(lod[0]['file'].casefold()), 'lods_ini_LOD_0'
    candidates = [p for p in kn5 if p.stem.casefold() == root.name.casefold()]
    if len(candidates) == 1:
        return candidates[0], 'same_name_as_car_directory'
    candidates = [p for p in kn5 if p.stem.casefold().endswith('_lod_a')]
    if len(candidates) == 1:
        return candidates[0], 'unique_lod_a'
    return None, 'ambiguous_or_missing_primary'


def inspect_car(car_dir: Path) -> dict:
    root = car_dir.resolve(strict=True)
    if not root.is_dir():
        raise InputError('car-dir must be a directory')
    if car_dir.is_symlink():
        raise InputError('car-dir symlink is not accepted')
    kn5 = sorted((p for p in root.iterdir() if p.suffix.casefold() == '.kn5'),
                 key=lambda p: p.name.casefold())
    if not kn5:
        raise InputError('No KN5 files in supplied car directory')
    if len(kn5) > MAX_KN5_FILES:
        raise InputError('Too many KN5 files for preflight')
    lods, warnings = _lod_ini(root)
    records: list[dict] = []
    for path in kn5:
        if path.is_symlink() or not path.is_file():
            raise InputError('KN5 symlink or unusual file type refused')
        size = path.stat().st_size
        if size <= 0 or size > MAX_KN5_BYTES:
            raise InputError(f'KN5 size outside supported preflight budget: {path.name}')
        records.append({'filename': path.name, 'bytes': size, 'sha256': _hash(path),
                        'is_collider': path.name.casefold() == 'collider.kn5'})
    primary, method = _select_primary(kn5, root, lods)
    if primary is None:
        warnings.append('Primary model cannot be selected safely; supply unpacked lods.ini')
    texture_dir = root / 'skins'
    skin_names: list[str] = []
    if texture_dir.is_dir() and not texture_dir.is_symlink():
        skin_names = sorted(p.name for p in texture_dir.iterdir()
                            if p.is_dir() and not p.is_symlink())[:128]
    return {
        'schema': 'outrun-ac-full-car-source-v1',
        'car_id': root.name,
        'status': 'SOURCE_DISCOVERED_NEEDS_BLENDER_IMPORT' if primary else 'BLOCKED_PRIMARY_KN5',
        'primary_model': primary.name if primary else None,
        'selection_method': method,
        'lods': lods,
        'kn5_files': records,
        'skins': skin_names,
        'warnings': warnings,
        'rights': 'Source asset rights must be confirmed before use or redistribution',
        'not_yet_verified': [
            'geometry', 'hierarchy', 'materials', 'textures', 'wheel_pivots',
            'OutRun PMT writer', 'game-runtime', 'VR-stereo'],
        'source_files_modified': False,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--car-dir', required=True, type=Path)
    p.add_argument('--output', type=Path, help='Optional local JSON manifest; no binary assets uploaded')
    args = p.parse_args(argv)
    try:
        report = inspect_car(args.car_dir)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n',
                                   encoding='utf-8')
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report['status'] == 'SOURCE_DISCOVERED_NEEDS_BLENDER_IMPORT' else 2
    except (InputError, OSError) as exc:
        print(f'BLOCKED_INPUT: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
