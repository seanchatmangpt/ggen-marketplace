import importlib.util, pathlib, unittest
P=pathlib.Path(__file__).parents[1]/"scripts"/"sensitivity.py"; s=importlib.util.spec_from_file_location("sensitivity",P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
class T(unittest.TestCase):
 def test_gamma_bounds(self):
  self.assertEqual(m.gamma_interval(2.0,2.0),(1.0,4.0)); self.assertTrue(m.robust_positive(2.0,3.0))
  with self.assertRaisesRegex(ValueError,"INVALID_GAMMA"): m.gamma_interval(1.0,.5)
