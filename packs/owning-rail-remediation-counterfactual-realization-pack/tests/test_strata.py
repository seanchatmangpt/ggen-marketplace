import importlib.util, pathlib, unittest
P=pathlib.Path(__file__).parents[1]/"scripts"/"strata.py"; s=importlib.util.spec_from_file_location("strata",P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
class T(unittest.TestCase):
 def test_worst_stratum_dominates(self):
  rows=[("a",2.0),("a",2.0),("b",-1.0)]
  self.assertEqual(m.worst_stratum(rows),("b",-1.0)); self.assertFalse(m.all_nonnegative(rows))
