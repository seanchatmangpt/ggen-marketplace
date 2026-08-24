import unittest
from scripts.calibration import calibrate
class T(unittest.TestCase):
 def test_false_authentic(self):
  c=calibrate([1,1,0,1,0],[1,0,0,1,0]);self.assertEqual(c.state,"CALIBRATED");self.assertGreater(c.false_authentic,0)
