import importlib.util, pathlib, unittest
P=pathlib.Path(__file__).parents[1]/"scripts"/"frontier.py"; s=importlib.util.spec_from_file_location("frontier",P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
class T(unittest.TestCase):
 def test_split_current_refuses(self):
  self.assertEqual(m.current_model([(1,"a"),(2,"b")]),(2,"b"))
  with self.assertRaisesRegex(ValueError,"DIVERGENT_CALIBRATION_FRONTIER"): m.current_model([(2,"a"),(2,"b")])
