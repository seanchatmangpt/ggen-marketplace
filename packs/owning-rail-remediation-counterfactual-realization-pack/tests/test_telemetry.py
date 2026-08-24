import importlib.util, pathlib, unittest
P=pathlib.Path(__file__).parents[1]/"scripts"/"telemetry.py"; s=importlib.util.spec_from_file_location("telemetry",P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
class T(unittest.TestCase):
 def test_projection(self):
  e=m.project("p","a"*40,2.0,1.0,"PARTIAL_ALIVE")
  self.assertEqual(e["ocel:activity"],"remediation_counterfactual_realization"); self.assertFalse(e["actuation_performed"])
