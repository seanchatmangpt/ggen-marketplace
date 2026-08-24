import importlib.util, pathlib, sys, unittest
root=pathlib.Path(__file__).parents[1]/"scripts"
def load(name):
 spec=importlib.util.spec_from_file_location(name,root/f"{name}.py"); mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod); return mod
realization=load("realization"); calibration=load("calibration")
class T(unittest.TestCase):
 def test_calibrated_and_unreliable(self):
  good=[realization.Realization(1,1,.1) for _ in range(5)]
  self.assertEqual(calibration.calibrate(good).state,"CALIBRATED")
  bad=[realization.Realization(1,-1,.1) for _ in range(5)]
  self.assertEqual(calibration.calibrate(bad).state,"UNRELIABLE")
