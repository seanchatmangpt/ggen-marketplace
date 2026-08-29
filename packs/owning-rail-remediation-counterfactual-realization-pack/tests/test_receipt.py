import importlib.util, pathlib, sys, unittest
root=pathlib.Path(__file__).parents[1]/"scripts"
def load(name):
 spec=importlib.util.spec_from_file_location(name,root/f"{name}.py"); mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod); return mod
realization=load("realization"); calibration=load("calibration"); receipt=load("receipt"); replay=load("replay")
class T(unittest.TestCase):
 def test_receipt_replay_and_tamper(self):
  c=calibration.calibrate([realization.Realization(1,1,0) for _ in range(5)])
  r=receipt.manufacture("o/r@"+"a"*40,c,"PARTIAL_ALIVE")
  self.assertEqual(replay.replay(r),"REPLAY_MATCH")
  r["body"]["standing"]="ALIVE"
  with self.assertRaisesRegex(ValueError,"RECEIPT_MISMATCH"): replay.replay(r)
