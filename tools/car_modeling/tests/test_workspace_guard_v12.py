"""Safety regression: dynamic A/C Ferrari workpack and import-only bootstrapping."""
import importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"tools"/"car_modeling"/"workspace_guard.py"
spec=importlib.util.spec_from_file_location("workspace_guard",MODULE)
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
SHA="a"*64
SEQ=["center_console","driver_controls","inner_door","visible_seat","instrument_cluster","dashboard","steering_wheel","cross_cockpit_qa"]
def fixture():
    queue={"repository":"thp32tt/imsi1","branch":"main",
        "active_by_slot":{"A":"360spider","C":"f355spider"},
        "cars":[{"id":"360spider","slot":"A","workpack_path":"docs/automation/FERRARI_COCKPIT_WORKPACK_A_360SPIDER.json"},
                {"id":"f355spider","slot":"C","workpack_path":"docs/automation/FERRARI_COCKPIT_WORKPACK_C_F355SPIDER.json"}],
        "strategy_v3":{"component_sequence":SEQ,"dispatch_turn_limit_per_component":2,"protected_regions":{"windshield_and_front_glass":"DO_NOT_EDIT"}}}
    w={"car_id":"360spider","slot":"A","component_order":SEQ,"current_component":"source_bootstrap","dispatches_on_component":0,
       "max_dispatches_per_component":2,"input_stage":"SOURCE_IMPORT_PENDING","original_game_resource_sha256":SHA,
       "original_import_blend_sha256":None,"migration_input_blend_sha256":None,
       "components":{**{k:{"status":"NOT_STARTED","source_edits_this_phase":0} for k in SEQ}, "source_bootstrap":{"status":"NOT_STARTED","source_edits_this_phase":0}}}
    return queue,w
class WorkpackV12Test(unittest.TestCase):
    def test_identity_source_only_valid(self):
        q,w=fixture()
        self.assertEqual(g.check_identity(q,w,"A",require_baseline=False),SEQ)
        with self.assertRaises(g.GuardError):g.preflight(q,w,"A")
    def test_source_sha_required(self):
        q,w=fixture();w["original_game_resource_sha256"]="bogus"
        with self.assertRaises(g.GuardError):g.check_identity(q,w,"A",require_baseline=False)
    def test_import_sha_enables_regular_geometry(self):
        q,w=fixture()
        w.update(input_stage="SOURCE_VERIFIED",original_import_blend_sha256=SHA,migration_input_blend_sha256=SHA,current_component="center_console")
        self.assertIn("PASS",g.preflight(q,w,"A"))
    def test_paths_follow_dynamic_active_vehicle(self):
        q,w=fixture()
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"docs"/"automation"
            p.mkdir(parents=True)
            (p/"FERRARI16_GEOMETRY_QUEUE.json").write_text(json.dumps(q))
            result=g.paths(Path(t),"A")
            self.assertEqual(result[1].name,"FERRARI_COCKPIT_WORKPACK_A_360SPIDER.json")
            q["cars"][0]["workpack_path"]="docs/automation/../secrets.json"
            (p/"FERRARI16_GEOMETRY_QUEUE.json").write_text(json.dumps(q))
            with self.assertRaises(g.GuardError):g.paths(Path(t),"A")
    def test_initial_p0_allowed_once_not_infinite_polish(self):
        q,w=fixture()
        w.update(input_stage="SOURCE_VERIFIED",original_import_blend_sha256=SHA,migration_input_blend_sha256=SHA,
                 current_component="steering_wheel")
        for k in SEQ[:SEQ.index("steering_wheel")]:
            w["components"][k]={"status":"COVERED_PARTIAL_QA","source_edits_this_phase":1}
        self.assertIn("PASS",g.preflight(q,w,"A"))
        w["components"]["steering_wheel"]["source_edits_this_phase"]=1
        with self.assertRaises(g.GuardError):g.preflight(q,w,"A")
    def test_source_bootstrap_checks_native_pmt_and_nothing_else(self):
        from unittest import mock
        import hashlib
        q,w=fixture()
        path="/home/chatgpt-runner/rea-input/outrun/outrun2006/Cars/obj_plcar_360sp_pmt.sz"
        data=b"verified original PMT synthetic fixture"
        w["original_game_resource_file"]=path
        w["original_game_resource_sha256"]=hashlib.sha256(data).hexdigest()
        with mock.patch.object(Path,"is_file",return_value=True), mock.patch.object(Path,"read_bytes",return_value=data):
            self.assertIn("PASS SOURCE_BOOTSTRAP",g.bootstrap_preflight(q,w,"A",path))
            with self.assertRaises(g.GuardError):
                g.bootstrap_preflight(q,w,"A","/tmp/fake_pmt.sz")

    def test_protected_window_never_editable(self):
        q,w=fixture()
        w.update(input_stage="SOURCE_VERIFIED",original_import_blend_sha256=SHA,migration_input_blend_sha256=SHA,current_component="windshield_frame")
        w["components"]["windshield_frame"]={"status":"NOT_STARTED","source_edits_this_phase":0}
        with self.assertRaises(g.GuardError):g.preflight(q,w,"A")
if __name__=="__main__": unittest.main()