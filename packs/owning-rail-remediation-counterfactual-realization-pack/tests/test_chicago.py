import importlib.util, pathlib, sys, unittest
root=pathlib.Path(__file__).parents[1]/"scripts"
def load(name):
 spec=importlib.util.spec_from_file_location(name,root/f"{name}.py"); mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod); return mod
realization=load("realization"); calibration=load("calibration"); standing=load("standing")
class T(unittest.TestCase):
 def test_owner_red_dominates_good_counterfactual_realization(self):
  c=calibration.calibrate([realization.Realization(1,1,0) for _ in range(10)])
  self.assertEqual(c.state,"CALIBRATED")
  self.assertEqual(standing.standing("BUILD_BROKEN",c.state,True,c.support),"BUILD_BROKEN")
  self.assertEqual(standing.standing("PASS",c.state,True,c.support),"PARTIAL_ALIVE")
