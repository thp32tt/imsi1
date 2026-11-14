"""Tests for AC complete-car source discovery. Synthetic bytes are NOT valid KN5 models."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'assetto_full_car_preflight.py'
spec = importlib.util.spec_from_file_location('ac_car_preflight', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InventoryTests(unittest.TestCase):
    def write_car(self, root, name='ferrari_360'):
        car = root / name
        car.mkdir()
        (car / f'{name}.kn5').write_bytes(b'KN5-main-test-dummy')
        (car / 'collider.kn5').write_bytes(b'KN5-collider-test-dummy')
        return car

    def test_same_name_primary_and_safely_ignored_collider(self):
        with tempfile.TemporaryDirectory() as tmp:
            car = self.write_car(Path(tmp))
            got = module.inspect_car(car)
            self.assertEqual(got['primary_model'], 'ferrari_360.kn5')
            self.assertEqual(got['status'], 'SOURCE_DISCOVERED_NEEDS_BLENDER_IMPORT')
            self.assertFalse(got['source_files_modified'])
            self.assertEqual(len(got['kn5_files']), 2)

    def test_primary_explicit_in_lods(self):
        with tempfile.TemporaryDirectory() as tmp:
            car = self.write_car(Path(tmp))
            (car / 'ferrari_360_lod_b.kn5').write_bytes(b'kn5-LOD-B')
            (car / 'data').mkdir()
            (car / 'data/lods.ini').write_text(
                '[LOD_0]\nFILE=ferrari_360.kn5\n[LOD_1]\nFILE=ferrari_360_lod_b.kn5\n')
            got = module.inspect_car(car)
            self.assertEqual(got['selection_method'], 'lods_ini_LOD_0')
            self.assertEqual(len(got['lods']), 2)

    def test_lod_a_without_name_is_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            car = Path(tmp) / 'ks_car'
            car.mkdir()
            (car / 'something_lod_a.kn5').write_bytes(b'kn5')
            (car / 'collider.kn5').write_bytes(b'collider')
            got = module.inspect_car(car)
            self.assertEqual(got['primary_model'], 'something_lod_a.kn5')

    def test_only_collider_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            car = Path(tmp) / 'ks_car'
            car.mkdir()
            (car / 'collider.kn5').write_bytes(b'collider')
            self.assertEqual(module.inspect_car(car)['status'], 'BLOCKED_PRIMARY_KN5')

    def test_reject_lod_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            car = self.write_car(Path(tmp))
            (car / 'data').mkdir()
            (car / 'data/lods.ini').write_text('[LOD_0]\nFILE=../../other.kn5\n')
            with self.assertRaises(module.InputError):
                module.inspect_car(car)

    def test_reject_missing_lod_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            car = self.write_car(Path(tmp))
            (car / 'data').mkdir()
            (car / 'data/lods.ini').write_text('[LOD_0]\nFILE=notthere.kn5\n')
            with self.assertRaises(module.InputError):
                module.inspect_car(car)

    def test_reject_symlink_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            car = self.write_car(Path(tmp))
            (car / 'bad.kn5').symlink_to('ferrari_360.kn5')
            with self.assertRaises(module.InputError):
                module.inspect_car(car)


if __name__ == '__main__':
    unittest.main()
