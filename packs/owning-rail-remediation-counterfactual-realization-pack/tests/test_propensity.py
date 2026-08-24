import importlib.util, pathlib, unittest
P=pathlib.Path(__file__).parents[1]/"scripts"/"propensity.py"
s=importlib.util.spec_from_file_location("propensity",P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
class T(unittest.TestCase):
 def test_estimators_and_support(self):
  self.assertAlmostEqual(m.horvitz_thompson([(1.0,2.0),(1.0,4.0)]),3.0)
  self.assertAlmostEqual(m.self_normalized([(0.5,2.0),(1.0,4.0)]),8/3)
  with self.assertRaisesRegex(ValueError,"PROPENSITY_SUPPORT"): m.horvitz_thompson([(0.0,1.0)])
