import unittest
from scripts.calibration import calibrate
class T(unittest.TestCase):
 def test_false_independent(self):
  c=calibrate(["INDEPENDENT"]*5,["INDEPENDENT"]*4+["DEPENDENT"]);self.assertEqual(c.state,"CALIBRATED");self.assertGreater(c.false_independent,0)
