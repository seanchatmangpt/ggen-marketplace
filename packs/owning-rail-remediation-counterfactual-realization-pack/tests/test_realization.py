import importlib.util, pathlib, sys, unittest
P=pathlib.Path(__file__).parents[1]/"scripts"/"realization.py"
s=importlib.util.spec_from_file_location("realization",P); m=importlib.util.module_from_spec(s); sys.modules["realization"]=m; s.loader.exec_module(m)
class T(unittest.TestCase):
    def test_false_safe_and_regression(self):
        r=m.Realization(2.0,-1.0,0.5)
        self.assertTrue(r.false_safe); self.assertEqual(r.state,"REGRESSED"); self.assertEqual(r.error,3.0)
