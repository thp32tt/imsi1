import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "workspace_guard.py"
spec = importlib.util.spec_from_file_location("workspace_guard", MODULE)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
H = "a" * 64
J = "b" * 64
K = "c" * 64
ORDER = ["center_console", "driver_controls", "inner_door", "visible_seat", "instrument_cluster", "dashboard", "steering_wheel", "cross_cockpit_qa"]


def fixture():
    queue = {"repository": "thp32tt/imsi1", "branch": "main", "active_by_slot": {"A": "daytona365", "C": "f50"},
             "strategy_v3": {"component_sequence": ORDER[:], "dispatch_turn_limit_per_component": 2,
                             "protected_regions": {"windshield_and_front_glass": "DO_NOT_EDIT"}}}
    comp = {n: {"status": "NOT_STARTED", "source_edits_this_phase": 0} for n in ORDER}
    for n in ORDER[:3]:
        comp[n] = {"status": "COVERED_PARTIAL_QA", "source_edits_this_phase": 1}
    comp["windshield_frame"] = {"status": "PROTECTED_REVERTED_DO_NOT_EDIT", "source_edits_this_phase": 1}
    workpack = {"slot": "C", "car_id": "f50", "component_order": ORDER[:], "components": comp,
                "current_component": "visible_seat", "dispatches_on_component": 0,
                "max_dispatches_per_component": 2, "original_game_resource_sha256": H,
                "original_import_blend_sha256": J, "migration_input_blend_sha256": K}
    receipt = {"slot": "C", "vehicle": "f50", "component": "visible_seat", "status": "COVERED_PARTIAL_QA",
               "full_vehicle_qa_pass": False, "native_original_pmt_sha256": H,
               "original_import_blend_sha256": J, "input_sha256": K, "output_sha256": H,
               "input_blend": "input.blend", "output_blend": "output.blend",
               "blender_saved": True, "independent_reopen": "PASS_SEPARATE_PROCESS",
               "source_mesh_fingerprints_before": {"PMT_f50_seat": H, "PMT_f50_glass": H},
               "source_mesh_fingerprints_after": {"PMT_f50_seat": J, "PMT_f50_glass": H},
               "modified_objects": ["PMT_f50_seat"], "original_mesh": "PMT_f50_seat",
               "unchanged_other_native_meshes": 1, "windshield_and_other_regions_untouched": True,
               "nonseat_components_within_target_unchanged": True,
               "changed_existing_vertices": 12, "exports": [], "new_textures": []}
    return queue, workpack, receipt


class GuardTests(unittest.TestCase):
    def test_valid_current_dispatch(self):
        q,w,_ = fixture()
        self.assertIn("PASS", guard.preflight(q,w,"C"))

    def test_unauthorized_slot_car_switch(self):
        q,w,_ = fixture()
        w["car_id"] = "daytona365"
        with self.assertRaises(guard.GuardError): guard.preflight(q,w,"C")

    def test_windshield_never_targetable(self):
        q,w,_ = fixture()
        w["current_component"] = "windshield_frame"
        with self.assertRaises(guard.GuardError): guard.preflight(q,w,"C")

    def test_reject_queued_protected_region(self):
        q,w,_ = fixture()
        q["strategy_v3"]["component_sequence"].append("windshield_frame")
        w["component_order"].append("windshield_frame")
        with self.assertRaises(guard.GuardError): guard.preflight(q,w,"C")

    def test_no_repeated_dispatch_after_cap(self):
        q,w,_ = fixture()
        w["dispatches_on_component"] = 2
        with self.assertRaises(guard.GuardError): guard.preflight(q,w,"C")

    def test_no_wheel_or_dashboard_polish(self):
        q,w,_ = fixture()
        w["current_component"] = "steering_wheel"
        w["components"]["steering_wheel"]["status"] = "IN_PROGRESS"
        with self.assertRaises(guard.GuardError): guard.preflight(q,w,"C")

    def test_fresh_reopen_receipt_passes(self):
        q,w,r = fixture()
        self.assertIn("PASS", guard.verify_receipt(q,w,"C",r))

    def test_extra_steering_change_is_rejected(self):
        q,w,r = fixture()
        r["source_mesh_fingerprints_after"]["PMT_f50_glass"] = K
        with self.assertRaises(guard.GuardError): guard.verify_receipt(q,w,"C",r)

    def test_false_full_qa_pass_rejected(self):
        q,w,r = fixture()
        r["full_vehicle_qa_pass"] = True
        with self.assertRaises(guard.GuardError): guard.verify_receipt(q,w,"C",r)

    def test_generated_object_rejected(self):
        q,w,r = fixture()
        r["source_mesh_fingerprints_before"]["GeneratedSeat"] = K
        r["source_mesh_fingerprints_after"]["GeneratedSeat"] = H
        r["modified_objects"].append("GeneratedSeat")
        r["unchanged_other_native_meshes"] = 1
        with self.assertRaises(guard.GuardError): guard.verify_receipt(q,w,"C",r)

    def test_user_protected_region_cannot_be_edited(self):
        q,w,r = fixture()
        r["modified_objects"] = ["PMT_f50_windshield_frame"]
        with self.assertRaises(guard.GuardError): guard.verify_receipt(q,w,"C",r)

    def test_source_package_hash_mismatch_rejected(self):
        q,w,r = fixture()
        r["native_original_pmt_sha256"] = K
        with self.assertRaises(guard.GuardError): guard.verify_receipt(q,w,"C",r)

    def test_blend_sha_verified_if_path_supplied(self):
        q,w,r = fixture()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"output.blend"
            path.write_bytes(b"original source-derived blend")
            with self.assertRaises(guard.GuardError): guard.verify_receipt(q,w,"C",r,path)


if __name__ == "__main__":
    unittest.main()
